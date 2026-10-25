from typing import Any
from uuid import UUID

from flask import Response
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.message import Message
from app.models.user import User
from app.models.user_message import UserMessage
from app.data_access.message import get_message_by_id, get_messages_by_sender_id, save_message, delete_message_from_db

from app.data_access.user_message import (
    get_user_message_by_id,
    get_user_messages_by_user_id,
    get_unread_count_by_user_id,
    save_user_messages,
    mark_user_message_as_read as mark_user_message_read,
    soft_delete_user_message as soft_delete_user_message_in_db
)

from app.schemas.message_schema import serialize_message
from app.schemas.user_message_schema import serialize_user_message

from app.utils.database import commit
from app.utils.responses import error_response, success_response
from app.utils.validators import is_valid_uuid


def create_message( data: dict[str, Any], sender_id: str) -> tuple[Response, int]:
    subject = data.get("subject")
    message_text = data.get("message")
    is_broadcast = data.get("is_broadcast", False)
    recipient_ids = data.get("recipient_ids", [])

    if not isinstance(subject, str) or not subject.strip():
        return error_response( message="Subject is required.", status_code=400 )

    if not isinstance(message_text, str) or not message_text.strip():
        return error_response( message="Message content is required.", status_code=400 )

    if not isinstance(is_broadcast, bool):
        return error_response( message="Invalid broadcast value.", status_code=400 )

    if not isinstance(recipient_ids, list):
        return error_response( message="Recipient IDs must be a list.", status_code=400 )

    if is_broadcast and recipient_ids:
        return error_response( message="Choose broadcast or individual recipients, not both.", status_code=400 )

    if not is_broadcast and not recipient_ids:
        return error_response( message="At least one recipient is required.", status_code=400 )

    if not is_valid_uuid(sender_id):
        return error_response( message="Invalid sender ID.", status_code=400 )

    sender_uuid = UUID(str(sender_id))
    sender = db.session.get(User, sender_uuid)

    if not sender or sender.role not in ("Admin", "Operator"):
        return error_response( message="Sender is not authorized to send messages.", status_code=403 )

    if is_broadcast:
        recipients = User.query.filter( User.role == "User", User.is_active.is_(True)).all()
    else:
        if any(
                not isinstance(recipient_id, str)
                or not is_valid_uuid(recipient_id)
                for recipient_id in recipient_ids
        ):
            return error_response(message="One or more recipient IDs are invalid.", status_code=400)

        recipient_uuids = {
            UUID(recipient_id)
            for recipient_id in recipient_ids
        }

        recipients = User.query.filter(
            User.id.in_(recipient_uuids),
            User.role == "User",
            User.is_active.is_(True)
        ).all()

        if len(recipients) != len(recipient_uuids):
            return error_response(message="One or more recipients are invalid or inactive.", status_code=400)

    if not recipients:
        return error_response(message="There are no eligible recipients.", status_code=400)

    message = Message( sender_id=sender_uuid, subject=subject.strip(), message=message_text.strip(), is_broadcast=is_broadcast )

    recipient_records = [ UserMessage( user_id=recipient.id, message=message ) for recipient in recipients ]

    try:
        save_message(message)
        db.session.flush()

        save_user_messages(recipient_records)
        commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return success_response( message="Message sent successfully.", data=serialize_message(message), status_code=201 )


def get_message_recipients() -> tuple[Response, int]:
    statement = (
        db.select(User)
        .where( User.role == "User", User.is_active.is_(True) )
        .order_by(User.first_name.asc(), User.last_name.asc())
    )

    recipients: list[User] = db.session.scalars(statement).all()

    data = [
        { "id": str(user.id), "first_name": user.first_name, "last_name": user.last_name, "email": user.email }
        for user in recipients
    ]

    return success_response( message="Message recipients retrieved successfully.", data=data, status_code=200 )

def get_user_messages(user_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(user_id):
        return error_response( message="Invalid user ID.", status_code=400 )

    user_uuid = UUID(str(user_id))
    user_messages = get_user_messages_by_user_id(user_uuid)

    data = [ serialize_user_message(user_message) for user_message in user_messages ]

    return success_response( message="Messages retrieved successfully.", data=data, status_code=200 )


def get_unread_count(user_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(user_id):
        return error_response( message="Invalid user ID.", status_code=400 )

    user_uuid = UUID(str(user_id))
    unread_count = get_unread_count_by_user_id(user_uuid)

    return success_response( message="Unread message count retrieved successfully.", data={"unread_count": unread_count}, status_code=200 )


def get_sent_messages(sender_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(sender_id):
        return error_response( message="Invalid sender ID.", status_code=400 )

    sender_uuid = UUID(str(sender_id))
    messages = get_messages_by_sender_id(sender_uuid)

    data = [
        serialize_message(message)
        for message in messages
    ]

    return success_response( message="Sent messages retrieved successfully.",  data=data, status_code=200 )


def mark_message_as_read( user_message_id: str, user_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(user_message_id) or not is_valid_uuid(user_id):
        return error_response( message="Invalid ID.", status_code=400 )

    user_message_uuid = UUID(str(user_message_id))
    user_uuid = UUID(str(user_id))

    user_message = get_user_message_by_id(user_message_uuid)

    if not user_message or user_message.user_id != user_uuid:
        return error_response( message="Message not found.", status_code=404 )

    if user_message.deleted_at is not None:
        return error_response( message="Message has been deleted.", status_code=404 )

    if user_message.read_at is None:
        try:
            mark_user_message_read(user_message)
            commit()

        except SQLAlchemyError:
            db.session.rollback()
            raise

    return success_response( message="Message marked as read.", data=serialize_user_message(user_message), status_code=200 )


def delete_user_message( user_message_id: str, user_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(user_message_id) or not is_valid_uuid(user_id):
        return error_response( message="Invalid ID.", status_code=400 )

    user_message_uuid = UUID(str(user_message_id))
    user_uuid = UUID(str(user_id))

    user_message = get_user_message_by_id(user_message_uuid)

    if not user_message or user_message.user_id != user_uuid:
        return error_response( message="Message not found.", status_code=404 )

    if user_message.deleted_at is not None:
        return error_response( message="Message has already been deleted.", status_code=404 )

    try:
        soft_delete_user_message_in_db(user_message)
        commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise

    return success_response( message="Message deleted successfully.", status_code=200 )


def delete_message(message_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(message_id):
        return error_response( message="Invalid message ID.", status_code=400 )

    message_uuid = UUID(str(message_id))
    message = get_message_by_id(message_uuid)

    if not message:
        return error_response( message="Message not found.", status_code=404 )

    try:
        delete_message_from_db(message)
        commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise

    return success_response( message="Message deleted successfully.", status_code=200 )

