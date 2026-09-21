from typing import Any
from app.models.contact_message import ContactMessage
from app.schemas.user_schema import serialize_user


def serialize_contact_message(message: ContactMessage) -> dict[str, Any]:
    return {
        "id": str(message.id),
        "user": serialize_user(message.user) if message.user_id else None,
        "name": message.name,
        "email": message.email,
        "subject": message.subject,
        "message": message.message,
        "status": message.status,
        "created_at": message.created_at.isoformat(),
        "updated_at": message.updated_at.isoformat()
    }


def serialize_contact_messages(messages: list[ContactMessage]) -> list[dict[str, Any]]:
    return [serialize_contact_message(message) for message in messages]



