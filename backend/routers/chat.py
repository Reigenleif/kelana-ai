from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.chat import ConversationCreate, ConversationOut, MessageCreate, MessageOut
    from models.user import User
    from services.auth_service import get_current_user
    from services.chat_service import (
        create_conversation,
        get_conversation_messages,
        list_conversations,
        send_message,
        stream_message_service,
    )
except ImportError:
    from backend.database import get_db
    from backend.models.chat import ConversationCreate, ConversationOut, MessageCreate, MessageOut
    from backend.models.user import User
    from backend.services.auth_service import get_current_user
    from backend.services.chat_service import (
        create_conversation,
        get_conversation_messages,
        list_conversations,
        send_message,
        stream_message_service,
    )

router = APIRouter(tags=["AI Travel Chat & Conversations"])


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_conversations(db, current_user.id)


@router.post("/conversations", response_model=ConversationOut)
def create_conversation_endpoint(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_conversation(db, current_user.id, conv_in.title)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageOut],
)
def get_messages_endpoint(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversation_messages(db, conversation_id, current_user.id)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageOut],
)
def send_message_endpoint(
    conversation_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return send_message(db, conversation_id, current_user.id, msg_in)


@router.post("/conversations/{conversation_id}/messages/stream")
def stream_message_endpoint(
    conversation_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return StreamingResponse(
        stream_message_service(db, conversation_id, current_user.id, msg_in),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
