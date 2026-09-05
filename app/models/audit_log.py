from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("users.id"),nullable=True)

    action = db.Column(db.String(100), nullable=False)
    entity_name = db.Column(db.String(100), nullable=True)
    entity_id = db.Column(db.UUID(as_uuid=True), nullable=True)

    actor = db.Column(db.JSON, nullable=True)

    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="SUCCESS")



