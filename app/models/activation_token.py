from app.extensions import db
from app.models.base import BaseModel

class ActivationToken(BaseModel):
    __tablename__ = "activation_tokens"

    user_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("users.id"),nullable=False)

    token_hash = db.Column(db.String(255),nullable=False,unique=True)

    expires_at = db.Column(db.DateTime(timezone=True),nullable=False)

    user = db.relationship("User",back_populates="activation_tokens")
