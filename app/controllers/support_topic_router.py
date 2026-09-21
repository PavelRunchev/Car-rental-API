from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.decorators.roles_required import roles_required
from app.services.support_topic_service import (
    create_support_topic,
    get_all_support_topics,
    get_support_topic,
    update_support_topic_status,
)


support_topic_bp = Blueprint("support_topics", __name__, url_prefix="/api/support/topics" )


@support_topic_bp.route("", methods=["POST"])
@jwt_required()
def post_support_topic():
    data = request.get_json(silent=True)
    return create_support_topic(data)


@support_topic_bp.route("", methods=["GET"])
def get_support_topics():
    return get_all_support_topics()


@support_topic_bp.route("/<string:topic_id>", methods=["GET"])
def get_support_topic_by_id(topic_id: str):
    return get_support_topic(topic_id)


@support_topic_bp.route("/<string:topic_id>/status", methods=["PATCH"])
@jwt_required()
@roles_required("Admin", "Operator")
def patch_support_topic_status(topic_id: str):
    data = request.get_json(silent=True)
    return update_support_topic_status(topic_id, data)


