from typing import Any

from flask import Response, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.data_access.contact_message import save_contact_message, get_contact_messages, get_contact_message_by_id, update_contact_message_status
from app.models.contact_message import ContactMessage
from app.schemas.contact_message_schema import serialize_contact_message, serialize_contact_messages
from app.utils.responses import error_response, success_response
from app.utils.validators import validate_contact_message, validate_contact_message_status
from app.services.user_service import get_user_by_id


def create_contact_message(data: dict[str, Any]) -> tuple[Response, int]:
    print(data)
    if not data:
        return error_response( message="Request body must contain JSON data.", status_code=400 )

    errors: dict[str, str] = validate_contact_message(data)

    if errors:
        return error_response( message="Validation failed.", status_code=400, errors=errors )

    user_id = None

    authorization = request.headers.get("Authorization")
    print(authorization)
    if authorization:
        verify_jwt_in_request()

        jwt_user_id = get_jwt_identity()
        user = get_user_by_id(jwt_user_id)

        if not user:
            return error_response( message="User not found.", status_code=401 )

        if not user.is_active:
            return error_response(  message="User account is inactive.", status_code=403 )

        user_id = user.id

    print("save message")
    contact_message: ContactMessage = ContactMessage(
        user_id=user_id,
        name=data["name"].strip(),
        email=data["email"].strip().lower(),
        subject=data["subject"].strip(),
        message=data["message"].strip(),
        status="New",
    )

    save_contact_message(contact_message)

    return success_response(
        message="Your message has been sent successfully.",
        data=serialize_contact_message(contact_message),
        status_code=201
    )


def get_all_contact_messages() -> tuple[Response, int]:
    return success_response(data=serialize_contact_messages(get_contact_messages()), status_code=200)


def update_contact_message( contact_message_id: str, data: dict[str, Any] ) -> tuple[Response, int]:
    errors: dict[str, str] = validate_contact_message_status(data)

    if errors:
        return error_response( message="Validation failed.", status_code=400, errors=errors )

    contact_message: ContactMessage | None = get_contact_message_by_id( contact_message_id )

    if not contact_message:
        return error_response( message="Contact message not found.",  status_code=404 )

    if contact_message.status == data["status"]:
        return error_response( message="Contact message already has this status.", status_code=409 )

    old_status = contact_message.status

    contact_message.status = data["status"]

    update_contact_message_status(contact_message)

    return success_response(
        message="Contact message status updated successfully.",
        data=serialize_contact_message(contact_message),
        status_code=200
    )

