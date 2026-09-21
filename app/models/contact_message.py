from app import db
from app.models.base import BaseModel


class ContactMessage(BaseModel):
    __tablename__ = "contact_messages"

    user_id = db.Column( db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True )

    name = db.Column( db.String(100), nullable=False )

    email = db.Column( db.String(255), nullable=False)

    subject = db.Column( db.String(150), nullable=False )

    message = db.Column( db.Text, nullable=False )

    status = db.Column(
        db.Enum( "New", "Read", "Replied", "Closed", name="contact_message_status" ),
        nullable=False,
        default="New",
    )

    user = db.relationship("User")
