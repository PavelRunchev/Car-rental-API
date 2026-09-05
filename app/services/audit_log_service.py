from app.models.user import User
from flask import request

from app.extensions import db
from app.models.audit_log import AuditLog


def log_entity_action( action: str, user: User, entity_name: str | None = None,
    entity_id: str | None = None, old_values: dict | None = None,
    new_values: dict | None = None, status: str = "SUCCESS"
) -> None:

    actor: dict[str, str] = {
        "id": str(user.id),
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "role": user.role
    }

    audit = AuditLog(
        user_id=user.id,
        action=action,
        entity_name=entity_name,
        entity_id=entity_id,
        actor=actor,
        endpoint=request.path,
        method=request.method,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        old_values=old_values,
        new_values=new_values,
        status=status
    )

    db.session.add(audit)
    db.session.commit()