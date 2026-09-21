from typing import Any

from flask import Response
from flask_jwt_extended import get_jwt_identity

from app.models.support_topic import SupportTopic
from app.schemas.support_topic_schema import serialize_support_topic, serialize_support_topics
from app.data_access.support_topic_data import get_support_topic_by_id, get_support_topics, save_support_topic, update_support_topic
from app.utils.validators import validate_support_topic, validate_support_topic_status
from app.utils.responses import error_response, success_response
from app.services.user_service import get_user_by_id


def create_support_topic(data: dict[str, Any]) -> tuple[Response, int]:
    if not data:
        return error_response( message="Request body must contain JSON data.", status_code=400 )

    errors: dict[str, str] = validate_support_topic(data)
    if errors:
        return error_response( message="Validation failed.", status_code=400, errors=errors )

    user_id: str = get_jwt_identity()
    user = get_user_by_id(user_id)

    if not user:
        return error_response( message="User not found.", status_code=401 )

    if not user.is_active:
        return error_response( message="User account is inactive.",  status_code=403 )

    topic: SupportTopic = SupportTopic(
        user_id=user.id,
        title=data["title"].strip(),
        category=data["category"],
        status="Open"
    )

    save_support_topic(topic)

    return success_response(
        message="Support topic created successfully.",
        data=serialize_support_topic(topic),
        status_code=201,
    )


def get_all_support_topics() -> tuple[Response, int]:
    topics: list[SupportTopic] = get_support_topics()
    return success_response( data=serialize_support_topics(topics), status_code=200 )


def get_support_topic(topic_id: str) -> tuple[Response, int]:
    topic: SupportTopic | None = get_support_topic_by_id(topic_id)

    if not topic:
        return error_response( message="Support topic not found.", status_code=404 )

    return success_response( data=serialize_support_topic(topic), status_code=200 )


def update_support_topic_status(topic_id: str,data: dict[str, Any]) -> tuple[Response, int]:
    if not data:
        return error_response( message="Request body must contain JSON data.", status_code=400 )

    errors: dict[str, str] = validate_support_topic_status(data)
    if errors:
        return error_response( message="Validation failed.",  status_code=400,  errors=errors )

    topic: SupportTopic | None = get_support_topic_by_id(topic_id)
    if not topic:
        return error_response( message="Support topic not found.", status_code=404 )

    if topic.status == data["status"]:
        return error_response( message="Support topic already has this status.", status_code=409 )

    topic.status = data["status"]
    update_support_topic(topic)

    return success_response(
        message="Support topic status updated successfully.",
        data=serialize_support_topic(topic),
        status_code=200,
    )