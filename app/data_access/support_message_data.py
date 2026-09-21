from app.extensions import db
from app.models.support_message import SupportMessage
from app.utils.database import commit
from app.utils.validators import is_valid_uuid


def get_support_message_by_id(message_id: str) -> SupportMessage | None:
    if not is_valid_uuid(message_id):
        return None

    return db.session.get(SupportMessage, message_id)


def get_support_messages_by_topic(topic_id: str) -> list[SupportMessage]:
    return SupportMessage.query.filter_by(topic_id=topic_id).order_by(SupportMessage.created_at.asc()).all()


def save_support_message(message: SupportMessage) -> SupportMessage:
    db.session.add(message)
    commit()
    return message


def delete_support_message(message: SupportMessage) -> None:
    db.session.delete(message)
    commit()





    