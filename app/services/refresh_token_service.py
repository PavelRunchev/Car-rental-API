from __future__ import annotations
from flask import request
from app.extensions import db
from datetime import datetime
from app.models.refresh_token import RefreshToken
from app.utils import datetime_utils
from app.utils.database import commit
from app.models.user import User
from app.utils.jwt_utils import hash_token, get_refresh_token_expiration, create_access_token_for_user, create_refresh_token_for_user


def save_refresh_token(user: User,refresh_token: str,device_name: str | None = None,ip_address: str | None = None,user_agent: str | None = None) -> RefreshToken:
    token_hash = hash_token(refresh_token)
    expires_at = get_refresh_token_expiration()

    return create_refresh_token(
        user_id=str(user.id),
        token_hash=token_hash,
        expires_at=expires_at,
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent
    )


def create_refresh_token(user_id: str,token_hash: str,expires_at: datetime,device_name: str | None = None,ip_address: str | None = None,user_agent: str | None = None) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
        last_used_at=datetime_utils.utc_now(),
    )

    db.session.add(refresh_token)
    commit()
    return refresh_token


def find_refresh_token_by_hash(token_hash: str) -> RefreshToken | None:
    return RefreshToken.query.filter_by(token_hash=token_hash).first()


def delete_refresh_token(refresh_token: RefreshToken) -> None:
    db.session.delete(refresh_token)
    commit()


def delete_user_refresh_tokens(user_id: str) -> None:
    RefreshToken.query.filter_by(user_id=user_id).delete()
    commit()


def update_last_used(refresh_token: RefreshToken) -> RefreshToken:
    refresh_token.last_used_at = datetime_utils.utc_now()
    commit()
    return refresh_token


def cleanup_expired_tokens() -> int:
    deleted = (RefreshToken.query
        .filter(RefreshToken.expires_at < datetime_utils.utc_now()).delete())
    commit()
    return deleted


def generate_auth_tokens(user: User) -> dict:
    access_token = create_access_token_for_user(user)
    refresh_token = create_refresh_token_for_user(user)

    save_refresh_token(
        user=user,
        refresh_token=refresh_token,
        device_name=None,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    return { "access_token": access_token,"refresh_token": refresh_token }

