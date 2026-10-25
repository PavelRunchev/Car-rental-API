from typing import Any
from app.models.message import Message

def serialize_message(message: Message) -> dict[str, Any]:
    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "subject": message.subject,
        "message": message.message,
        "is_broadcast": message.is_broadcast,
        "created_at": message.created_at.isoformat(),
        "updated_at": message.updated_at.isoformat()
    }