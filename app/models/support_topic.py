from app.extensions import db
from app.models.base import BaseModel

class SupportTopic(BaseModel):
    __tablename__ = "support_topics"

    user_id = db.Column( db.UUID(as_uuid=True),  db.ForeignKey("users.id"), nullable=False )

    title = db.Column( db.String(150), nullable=False )

    category = db.Column(
        db.Enum("Payment", "Reservation", "Car", "Account", "Technical", "Other", name="support_topic_category"),
        nullable=False,
    )

    status = db.Column(
        db.Enum( "Open", "Closed", "Blocked", name="support_topic_status" ),
        nullable=False,
        default="Open"
    )

    user = db.relationship("User", back_populates="support_topics")
    messages = db.relationship( "SupportMessage",  back_populates="topic", cascade="all, delete-orphan" )






