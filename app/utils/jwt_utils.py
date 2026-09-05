from __future__ import annotations

from datetime import timedelta, datetime
from hashlib import sha256
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.utils import datetime_utils


ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRES = timedelta(days=30)


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def create_access_token_for_user(user: User) -> str:
    return create_access_token(identity=str(user.id),expires_delta=ACCESS_TOKEN_EXPIRES)


def create_refresh_token_for_user(user: User) -> str:
    return create_refresh_token(identity=str(user.id),expires_delta=REFRESH_TOKEN_EXPIRES)

def get_refresh_token_expiration() -> datetime:
    return datetime_utils.utc_now() + REFRESH_TOKEN_EXPIRES