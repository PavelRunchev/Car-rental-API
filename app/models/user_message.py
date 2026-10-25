from app.extensions import db
from app.models.base import BaseModel


class UserMessage(BaseModel):
    __tablename__ = "user_messages"

    message_id = db.Column( db.UUID(as_uuid=True), db.ForeignKey("messages.id"),  nullable=False, index=True )

    user_id = db.Column( db.UUID(as_uuid=True),  db.ForeignKey("users.id"), nullable=False, index=True )

    read_at = db.Column( db.DateTime(timezone=True), nullable=True )

    deleted_at = db.Column( db.DateTime(timezone=True), nullable=True )

    message = db.relationship( "Message", back_populates="recipients" )

    user = db.relationship( "User", backref=db.backref("received_messages", lazy="select") )

    __table_args__ = (
        db.UniqueConstraint(
            "message_id",
            "user_id",
            name="uq_user_message_recipient"
        ),
    )

    def __repr__(self):
        return   f"<UserMessage message_id={self.message_id} user_id={self.user_id}>"


