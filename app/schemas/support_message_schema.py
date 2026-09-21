from typing import Any

from app.models.support_message import SupportMessage
from app.schemas.user_schema import serialize_user


def serialize_support_message(message: SupportMessage) -> dict[str, Any]:
    return {
        "id": str(message.id),
        "user": serialize_user(message.user),
        "message": message.message,
        "created_at": message.created_at.isoformat(),
        "updated_at": message.updated_at.isoformat(),
    }


def serialize_support_messages(messages: list[SupportMessage]) -> list[dict[str, Any]]:
    return [ serialize_support_message(message) for message in messages ]

