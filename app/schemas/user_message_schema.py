from typing import Any
from app.models.user_message import UserMessage


def serialize_user_message(user_message: UserMessage) -> dict[str, Any]:
    return {
        "id": str(user_message.id),
        "message_id": str(user_message.message_id),
        "user_id": str(user_message.user_id),
        "read_at": ( user_message.read_at.isoformat() if user_message.read_at else None ),
        "deleted_at": ( user_message.deleted_at.isoformat() if user_message.deleted_at else None ),
        "created_at": user_message.created_at.isoformat(),
        "updated_at": user_message.updated_at.isoformat(),
        "message": {
            "id": str(user_message.message.id),
            "sender_id": str(user_message.message.sender_id),
            "subject": user_message.message.subject,
            "message": user_message.message.message,
            "is_broadcast": user_message.message.is_broadcast,
            "created_at": user_message.message.created_at.isoformat()
        }
    }

