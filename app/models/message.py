from app.extensions import db
from app.models.base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"

    sender_id = db.Column( db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False, index=True )

    subject = db.Column(db.String(255), nullable=False)

    message = db.Column(db.Text, nullable=False)

    is_broadcast = db.Column( db.Boolean, nullable=False, default=False, server_default=db.false() )

    sender = db.relationship( "User", foreign_keys=[sender_id])

    recipients = db.relationship( "UserMessage", back_populates="message", cascade="all, delete-orphan" )

    def __repr__(self):
        return f"<Message {self.subject}>"