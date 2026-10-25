from typing import Any

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.decorators.roles_required import roles_required
from app.services.message_service import (
    create_message,
    get_message_recipients,
    get_user_messages,
    get_unread_count,
    get_sent_messages,
    mark_message_as_read,
    delete_user_message,
    delete_message
)

from app.utils.responses import error_response


message_bp = Blueprint("message", __name__, url_prefix="/api/messages")


@message_bp.route("/recipients", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_message_recipients_route():
    return get_message_recipients()


@message_bp.route("create", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Operator")
def create_message_route():
    data: dict[str, Any] | None = request.get_json(silent=True)

    if not data:
        return error_response(message="Request body is required.", status_code=400)

    return create_message(data, get_jwt_identity())


@message_bp.route("/sent", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_sent_messages_route():
    return get_sent_messages(get_jwt_identity())


@message_bp.route("", methods=["GET"])
@jwt_required()
@roles_required("User")
def get_user_messages_route():
    return get_user_messages(get_jwt_identity())


@message_bp.route("/unread-count", methods=["GET"])
@jwt_required()
@roles_required("User")
def get_unread_count_route():
    return get_unread_count(get_jwt_identity())


@message_bp.route("/<string:user_message_id>/read", methods=["PATCH"])
@jwt_required()
@roles_required("User")
def mark_message_as_read_route(user_message_id: str):
    return mark_message_as_read(
        user_message_id,
        get_jwt_identity()
    )


@message_bp.route("/<string:user_message_id>", methods=["DELETE"])
@jwt_required()
@roles_required("User")
def delete_user_message_route(user_message_id: str):
    return delete_user_message(
        user_message_id,
        get_jwt_identity()
    )


@message_bp.route("/sent/<string:message_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "Operator")
def delete_message_route(message_id: str):
    return delete_message(message_id)
