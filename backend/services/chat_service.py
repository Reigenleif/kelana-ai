from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.chat import Conversation, ConversationOut, Message, MessageCreate, MessageOut
from services import bedrock_service


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

    # 2. Get history context for AI
    history_msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    history = [{"sender": m.sender, "text": m.text} for m in history_msgs[:-1]]

    # 3. Generate AI response
    ai_reply_text = bedrock_service.generate_chat_response(history, msg_in.text.strip())

    # 4. Save AI message
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
