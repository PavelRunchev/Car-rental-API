from typing import Any
from flask import Response
from flask_jwt_extended import get_jwt_identity

from app.data_access.support_message_data import (
    delete_support_message,
    get_support_message_by_id,
    get_support_messages_by_topic,
    save_support_message,
)
from app.services.audit_log_service import log_entity_action
from app.data_access.support_topic_data import get_support_topic_by_id
from app.services.user_service import get_user_by_id
from app.models.support_message import SupportMessage
from app.schemas.support_message_schema import serialize_support_message, serialize_support_messages
from app.utils.responses import error_response, success_response
from app.utils.validators import validate_support_message


def create_support_message(topic_id: str, data: dict[str, Any]) -> tuple[Response, int]:
    if not data:
        return error_response(  message="Request body must contain JSON data.", status_code=400)

    errors = validate_support_message(data)
    if errors:
        return error_response(  message="Validation failed.",  status_code=400,  errors=errors )

    topic = get_support_topic_by_id(topic_id)

    if not topic:
        return error_response( message="Support topic not found.", status_code=404 )

    if topic.status != "Open":
        return error_response( message="Support topic is not open.", status_code=409 )

    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return error_response( message="User not found.", status_code=401 )

    if not user.is_active:
        return error_response( message="User account is inactive.", status_code=403 )

    support_message = SupportMessage(topic_id=topic.id, user_id=user.id, message=data["message"].strip())
    save_support_message(support_message)

    return success_response(
        message="Support message created successfully.",
        data=serialize_support_message(support_message),
        status_code=201
    )


def get_all_support_messages(topic_id: str) -> tuple[Response, int]:
    topic = get_support_topic_by_id(topic_id)
    if not topic:
        return error_response( message="Support topic not found.", status_code=404 )

    messages = get_support_messages_by_topic(topic.id)
    return success_response( data=serialize_support_messages(messages), status_code=200 )


def delete_support_message_by_id(message_id: str) -> tuple[Response, int]:
    support_message = get_support_message_by_id(message_id)
    if not support_message:
        return error_response( message="Support message not found.", status_code=404 )

    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)

    old_values = {
        "topic_id": str(support_message.topic_id),
        "user_id": str(support_message.user_id),
        "message": support_message.message,
        "created_at": support_message.created_at.isoformat(),
    }

    delete_support_message(support_message)

    log_entity_action(
        action="DELETE_SUPPORT_MESSAGE",
        user=user,
        entity_name="SupportMessage",
        entity_id=support_message.id,
        old_values=old_values,
        new_values=None,
    )

    return success_response( message="Support message deleted successfully.", status_code=200 )



