from datetime import datetime, timezone
from sqlalchemy import func
from app.extensions import db
from app.models.user_message import UserMessage


def get_user_message_by_id(user_message_id: str) -> UserMessage | None:
    return db.session.get(UserMessage, user_message_id)


def get_user_message_by_message_and_user( message_id: str, user_id: str) -> UserMessage | None:
    return UserMessage.query.filter_by( message_id=message_id, user_id=user_id ).first()

def get_user_messages_by_user_id(user_id: str) -> list[UserMessage]:
    return UserMessage.query.filter_by(user_id=user_id, deleted_at=None).order_by(UserMessage.created_at.desc()).all()


def get_unread_count_by_user_id(user_id: str) -> int:
    return (UserMessage.query
            .filter( UserMessage.user_id == user_id, UserMessage.read_at.is_(None), UserMessage.deleted_at.is_(None) )
            .count())




def save_user_message(user_message: UserMessage) -> UserMessage:
    db.session.add(user_message)
    return user_message


def save_user_messages( user_messages: list[UserMessage]) -> list[UserMessage]:
    db.session.add_all(user_messages)
    return user_messages


def mark_user_message_as_read(user_message: UserMessage) -> UserMessage:
    if user_message.read_at is None:
        user_message.read_at = datetime.now(timezone.utc)

    return user_message


def soft_delete_user_message(user_message: UserMessage) -> UserMessage:
    if user_message.deleted_at is None:
        user_message.deleted_at = datetime.now(timezone.utc)

    return user_message


def update_user_message_in_db( user_message: UserMessage ) -> UserMessage:
    return user_message


def delete_user_message_from_db(user_message: UserMessage) -> None:
    db.session.delete(user_message)