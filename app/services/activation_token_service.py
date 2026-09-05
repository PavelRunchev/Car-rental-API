from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from app.extensions import db
from app.models.user import User
from app.models.activation_token import ActivationToken

ACTIVATION_TOKEN_EXPIRATION_HOURS = 24


def create_activation_token(user: User) -> str:
    token: str = token_urlsafe(32)
    token_hash: str = sha256(token.encode()).hexdigest()

    expires_at = datetime.now(timezone.utc) + timedelta(hours=ACTIVATION_TOKEN_EXPIRATION_HOURS)

    activation_token = ActivationToken(user_id=user.id,token_hash=token_hash,expires_at=expires_at)

    db.session.add(activation_token)
    return token


def delete_activation_tokens_by_user(user_id: str) -> None:
    ActivationToken.query.filter_by(user_id=user_id).delete()