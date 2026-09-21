from app.extensions import db
from app.models.contact_message import ContactMessage
from app.utils.database import commit
from app.utils.validators import is_valid_uuid


def get_contact_messages() -> list[ContactMessage]:
    return ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()


def save_contact_message( contact_message: ContactMessage) -> ContactMessage:
    db.session.add(contact_message)
    commit()
    return contact_message


def get_contact_message_by_id(contact_message_id: str) -> ContactMessage | None:
    if not is_valid_uuid(contact_message_id):
        return None

    return db.session.get(ContactMessage, contact_message_id)


def update_contact_message_status(contact_message: ContactMessage) -> ContactMessage:
    commit()
    return contact_message

