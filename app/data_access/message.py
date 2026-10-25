from app.extensions import db
from app.models.message import Message


def get_message_by_id(message_id: str) -> Message | None:
    return db.session.get(Message, message_id)


def get_messages() -> list[Message]:
    return Message.query.order_by(Message.created_at.desc()).all()


def get_messages_by_sender_id(sender_id: str) -> list[Message]:
    return Message.query.filter_by(sender_id=sender_id).order_by(Message.created_at.desc()).all()


def save_message(message: Message) -> Message:
    db.session.add(message)
    return message



def update_message_in_db(message: Message) -> Message:
    return message


def delete_message_from_db(message: Message) -> None:
    db.session.delete(message)