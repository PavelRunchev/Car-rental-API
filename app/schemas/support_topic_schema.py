from typing import Any

from app.models.support_topic import SupportTopic
from app.schemas.user_schema import serialize_user


def serialize_support_topic(topic: SupportTopic) -> dict[str, Any]:
    return {
        "id": str(topic.id),
        "user": serialize_user(topic.user),
        "title": topic.title,
        "category": topic.category,
        "status": topic.status,
        "created_at": topic.created_at.isoformat(),
        "updated_at": topic.updated_at.isoformat(),
    }


def serialize_support_topics(topics: list[SupportTopic]) -> list[dict[str, Any]]:
    return [ serialize_support_topic(topic) for topic in topics ]


