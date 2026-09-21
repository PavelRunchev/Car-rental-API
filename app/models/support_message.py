from app.extensions import db
from app.models.base import BaseModel

class SupportMessage(BaseModel):
    __tablename__ = "support_messages"

    topic_id = db.Column( db.UUID(as_uuid=True), db.ForeignKey("support_topics.id"), nullable=False )

    user_id = db.Column(  db.UUID(as_uuid=True), db.ForeignKey("users.id"),  nullable=False )

    message = db.Column(  db.Text,  nullable=False )

    topic = db.relationship( "SupportTopic",  back_populates="messages" )

    user = db.relationship("User")


