import json
from datetime import datetime
from typing import Generator

from fastapi import HTTPException, status
from models.chat import Conversation, ConversationOut, Message, MessageCreate, MessageOut
from services import bedrock_service
from sqlalchemy.orm import Session

DEFAULT_TITLES = {
    "Travel Planning",
    "Trip Planning Chat",
    "Trip Planning Session",
    "Kelana AI Travel Assistant",
    "Travel Assistant Chat",
    "New Chat",
}


def serialize_message(msg: Message) -> MessageOut:
    return MessageOut(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender=msg.sender,
        text=msg.text,
        created_at=msg.created_at,
    )


def serialize_conversation(conv: Conversation) -> ConversationOut:
    last_msg = None
    if conv.messages:
        last_msg = serialize_message(conv.messages[-1])

    return ConversationOut(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        last_message=last_msg,
    )


def get_or_create_default_conversation(db: Session, user_id: int) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).first()
    if not conv:
        conv = Conversation(
            user_id=user_id,
            title="Kelana AI Travel Assistant",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # Initial welcome message from AI Agent
        welcome_msg = Message(
            conversation_id=conv.id,
            sender="assistant",
            text="Hello! I am your Kelana AI Travel Assistant. Where would you like to travel, or do you need help planning a destination and itinerary?",
            created_at=datetime.utcnow(),
        )
        db.add(welcome_msg)
        db.commit()
        db.refresh(conv)
    return conv


def list_conversations(db: Session, user_id: int) -> list[ConversationOut]:
    get_or_create_default_conversation(db, user_id)
    convs = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()
    return [serialize_conversation(c) for c in convs]


def create_conversation(db: Session, user_id: int, title: str | None = None) -> ConversationOut:
    conv = Conversation(
        user_id=user_id,
        title=title or "Trip Planning Chat",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    welcome_msg = Message(
        conversation_id=conv.id,
        sender="assistant",
        text="Hello! I'm your Kelana AI Travel Assistant. How can I help with your upcoming journey?",
        created_at=datetime.utcnow(),
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(conv)

    return serialize_conversation(conv)


def get_conversation_messages(db: Session, conversation_id: int, user_id: int) -> list[MessageOut]:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    return [serialize_message(m) for m in messages]


def maybe_infer_conversation_title(db: Session, conv: Conversation, user_message_text: str) -> str | None:
    """
    Checks if conversation has default title or is the first user message,
    and infers a title capped at 3 words.
    """
    user_msg_count = db.query(Message).filter(
        Message.conversation_id == conv.id,
        Message.sender == "user",
    ).count()

    if user_msg_count <= 1 or conv.title in DEFAULT_TITLES:
        inferred = bedrock_service.infer_conversation_title(user_message_text)
        words = inferred.split()[:3]
        new_title = " ".join(words)
        if new_title:
            conv.title = new_title
            db.commit()
            db.refresh(conv)
            return conv.title
    return None


def send_message(db: Session, conversation_id: int, user_id: int, msg_in: MessageCreate) -> list[MessageOut]:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # 1. Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        sender="user",
        text=msg_in.text.strip(),
        created_at=datetime.utcnow(),
    )
    db.add(user_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user_msg)

    # 2. Check and infer title if first user message
    maybe_infer_conversation_title(db, conv, msg_in.text.strip())

    # 3. Get history context for AI
    history_msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    history = [{"sender": m.sender, "text": m.text} for m in history_msgs[:-1]]

    # 4. Generate AI response
    ai_reply_text = bedrock_service.generate_chat_response(history, msg_in.text.strip())

    # 5. Save AI message
    ai_msg = Message(
        conversation_id=conversation_id,
        sender="assistant",
        text=ai_reply_text,
        created_at=datetime.utcnow(),
    )
    db.add(ai_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ai_msg)

    return [serialize_message(user_msg), serialize_message(ai_msg)]


def stream_message_service(
    db: Session, conversation_id: int, user_id: int, msg_in: MessageCreate
) -> Generator[str, None, None]:
    """
    Streams AI response chunk-by-chunk using Server-Sent Events (SSE).
    Saves user message, optionally updates conversation title (max 3 words),
    streams chunks, and saves completed assistant message to the database.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        yield f"data: {json.dumps({'type': 'error', 'detail': 'Conversation not found'})}\n\n"
        return

    # 1. Persist user message to database immediately
    user_msg = Message(
        conversation_id=conversation_id,
        sender="user",
        text=msg_in.text.strip(),
        created_at=datetime.utcnow(),
    )
    db.add(user_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user_msg)

    # Emit saved user message
    yield f"data: {json.dumps({'type': 'user_message', 'message': serialize_message(user_msg).model_dump(mode='json')})}\n\n"

    # 2. Check if conversation title should be inferred (max 3 words)
    new_title = maybe_infer_conversation_title(db, conv, msg_in.text.strip())
    if new_title:
        yield f"data: {json.dumps({'type': 'title', 'title': new_title})}\n\n"

    # 3. Retrieve conversation history for LLM context
    history_msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    history = [{"sender": m.sender, "text": m.text} for m in history_msgs[:-1]]

    # 4. Stream chunks from Bedrock
    full_response_parts = []
    try:
        for chunk in bedrock_service.stream_chat_response(history, msg_in.text.strip()):
            full_response_parts.append(chunk)
            yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
    except Exception as e:
        print(f"Error during response stream: {e}")
        error_msg = "\n\n*(An interruption occurred during streaming)*"
        full_response_parts.append(error_msg)
        yield f"data: {json.dumps({'type': 'chunk', 'text': error_msg})}\n\n"

    # 5. Persist completed assistant message to database
    full_ai_text = "".join(full_response_parts).strip()
    if not full_ai_text:
        full_ai_text = "I'm here to assist with your travel questions. Please ask anything about destinations, flights, or itineraries!"

    ai_msg = Message(
        conversation_id=conversation_id,
        sender="assistant",
        text=full_ai_text,
        created_at=datetime.utcnow(),
    )
    db.add(ai_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ai_msg)

    # 6. Emit done event with saved assistant message & current title
    yield f"data: {json.dumps({'type': 'done', 'message': serialize_message(ai_msg).model_dump(mode='json'), 'title': conv.title})}\n\n"

