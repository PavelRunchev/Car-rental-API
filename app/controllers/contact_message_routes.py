from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.decorators.roles_required import roles_required
from app.services.contact_message_service import create_contact_message, get_all_contact_messages, update_contact_message

contact_bp = Blueprint("contact",  __name__, url_prefix="/api/contact-messages")

@contact_bp.route("", methods=["POST"])
def post_contact_message():
    data = request.get_json(silent=True)
    return create_contact_message(data)


@contact_bp.route("", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_contact_messages():
    return get_all_contact_messages()


@contact_bp.route("/<string:contact_message_id>/status", methods=["PATCH"])
@jwt_required()
@roles_required("Admin", "Operator")
def patch_contact_message_status(contact_message_id: str):
    data = request.get_json(silent=True)
    return update_contact_message( contact_message_id, data )
