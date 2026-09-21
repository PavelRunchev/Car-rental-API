from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.decorators.roles_required import roles_required
from app.services.support_message_service import create_support_message, delete_support_message_by_id, get_all_support_messages

support_message_bp = Blueprint("support_messages", __name__, url_prefix="/api/support/topics")


@support_message_bp.route("/<string:topic_id>/messages", methods=["POST"])
@jwt_required()
def post_support_message(topic_id: str):
    data = request.get_json(silent=True)
    return create_support_message(topic_id, data)


@support_message_bp.route("/<string:topic_id>/messages", methods=["GET"])
def get_support_messages(topic_id: str):
    return get_all_support_messages(topic_id)


@support_message_bp.route("/messages/<string:message_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "Operator")
def delete_support_message(message_id: str):
    return delete_support_message_by_id(message_id)



