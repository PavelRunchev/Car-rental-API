from app.extensions import db
from app.models.base import BaseModel


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = db.Column(db.UUID,db.ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)

    token_hash = db.Column(db.String(255),nullable=False,unique=True,index=True)

    expires_at = db.Column(db.DateTime(timezone=True),nullable=False)

    device_name = db.Column(db.String(255),nullable=True)

    ip_address = db.Column(db.String(45),nullable=True)

    user_agent = db.Column(db.Text,nullable=True)

    last_used_at = db.Column(db.DateTime(timezone=True),nullable=True)

    user = db.relationship("User", backref=db.backref("refresh_tokens",cascade="all, delete-orphan",lazy=True))

    def __repr__(self):
        return f"<RefreshToken {self.user_id}>"