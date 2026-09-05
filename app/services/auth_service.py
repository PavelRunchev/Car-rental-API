from datetime import datetime, timezone
from hashlib import sha256
from app.extensions import db
from flask import Response
from typing import Any
from uuid import uuid4
from flask_jwt_extended import get_jwt_identity
from app.models import RefreshToken
from app.schemas.user_schema import serialize_user
from app.utils.responses import error_response, success_response
from app.utils.normalize import normalize_email, normalize_name, normalize_phone
from app.services.user_service import get_user_by_email, create_user, get_user_by_id
from app.models.user import User
from app.models.activation_token import ActivationToken

from app.utils.validators import validate_register, validate_login, validate_refresh_token, validate_operator_user, is_valid_password
from app.services.refresh_token_service import find_refresh_token_by_hash, delete_refresh_token, generate_auth_tokens
from app.utils.jwt_utils import hash_token
from app.utils.datetime_utils import utc_now
from app.services.audit_log_service import log_entity_action


def register(data: dict[str, Any]) -> tuple[Response, int]:
    errors = validate_register(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    first_name = normalize_name(data["first_name"])
    last_name = normalize_name(data["last_name"])
    email = normalize_email(data["email"])
    phone = normalize_phone(data.get("phone"))
    password = data["password"]

    existing_user = get_user_by_email(email)

    if existing_user:
        return error_response(message="Email already exists.",status_code=409)

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        role="User",
        is_active=True,
        must_set_password=False
    )

    user.set_password(password)
    create_user(user)
    log_entity_action( action="REGISTER", user=user )

    return success_response(message="User registered successfully.", status_code=201, data=serialize_user(user))


def login(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict = validate_login(data)
    if errors:
        return error_response(message="Validation failed.", status_code=400, errors=errors)

    email: str = normalize_email(data["email"])
    password: str = data["password"]

    user: User | None = get_user_by_email(email)

    if not user:
        log_entity_action(action="LOGIN",entity_name="User", user=user,status="FAILED")
        return error_response(message="Invalid email or password.",status_code=401)

    if not user.is_active:
        return error_response(message="Your account has been deactivated.",status_code=403)

    if not user.check_password(password):
        log_entity_action(action="LOGIN",user=user,status="FAILED")
        return error_response(message="Invalid email or password.",status_code=401)

    tokens: dict[str, str] = generate_auth_tokens(user)
    log_entity_action( action="LOGIN", user=user )

    return success_response( message="Login successful.", data={ **tokens, "user": serialize_user(user) } )


def create_user_by_operator(data: dict[str, Any]) -> tuple[Response, int]:
    errors = validate_operator_user(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    operator_id: str = get_jwt_identity()
    operator: User | None = get_user_by_id(operator_id)

    if not operator:
        return error_response(message="User not found.",status_code=404)

    if operator.role not in {"Admin", "Operator"}:
        return error_response( message="Administrator or operator privileges are required.",status_code=403 )

    if not operator.is_active:
        return error_response( message="User is inactive.", status_code=403 )

    first_name = normalize_name(data["first_name"])
    last_name = normalize_name(data["last_name"])
    email = normalize_email(data["email"])
    phone = normalize_phone(data.get("phone"))

    existing_user = get_user_by_email(email)

    if existing_user:
        return error_response(message="Email already exists.",status_code=409)

    user = User(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=None,
        must_set_password=True,
        role="User",
        is_active=False
    )

    create_user(user)

    log_entity_action(
        action="CREATE_USER",
        user=operator,
        entity_name="User",
        entity_id=user.id,
        new_values={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "must_set_password": user.must_set_password
        }
    )

    return success_response( message="User created successfully. Password setup is required.", status_code=201, data=serialize_user(user))


def refresh(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_refresh_token(data)
    if errors:
        return error_response(message="Validation failed", status_code=400, errors=errors)

    refresh_token: str = data["refresh_token"]
    token_hash: str = hash_token(refresh_token)

    stored_token: RefreshToken | None = find_refresh_token_by_hash(token_hash)
    if not stored_token:
        return error_response(message="Invalid refresh token.", status_code=401)

    if stored_token.expires_at <= utc_now():
        delete_refresh_token(stored_token)
        return error_response(message="Refresh token has expired.",status_code=401)

    user: User | None = get_user_by_id(stored_token.user_id)
    if not user:
        delete_refresh_token(stored_token)
        return error_response(message="User not found.", status_code=401)

    if not user.is_active:
        delete_refresh_token(stored_token)
        return error_response(message="Your account has been deactivated.",status_code=403)

    delete_refresh_token(stored_token)
    tokens: dict[str, str] = generate_auth_tokens(user)
    log_entity_action(action="REFRESH",user=user)
    return success_response(message="Token refreshed.", data=tokens)


def logout(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_refresh_token(data)

    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    refresh_token: str = data["refresh_token"]
    token_hash: str = hash_token(refresh_token)
    stored_token: RefreshToken | None = find_refresh_token_by_hash(token_hash)

    if not stored_token:
        return error_response(message="Invalid refresh token.",status_code=401)

    user: User | None = get_user_by_id(stored_token.user_id)
    delete_refresh_token(stored_token)

    if user:
        log_entity_action(action="LOGOUT",user=user)

    return success_response(message="Logout successful.")


def activate_account(data: dict[str, Any]) -> tuple[Response, int]:
    token: str | None = data.get("token")
    password: str | None = data.get("password")

    if not token:
        return error_response(message="Activation token is required.",status_code=400)

    if not password:
        return error_response(message="Password is required.",status_code=400)

    if not is_valid_password(password):
        return error_response(message="Invalid password.",status_code=400)

    token_hash = sha256(token.encode()).hexdigest()

    activation_token: ActivationToken | None = (ActivationToken.query.filter_by(token_hash=token_hash).first())
    if not activation_token:
        return error_response(message="Invalid activation token.",status_code=400)


    now = datetime.now(timezone.utc)
    if activation_token.expires_at <= now:
        return error_response(message="Activation token has expired.",status_code=400)

    user = get_user_by_id(activation_token.user_id)
    if not user:
        return error_response(message="User not found.",status_code=404)

    if not user.must_set_password:
        return error_response(message="Account has already been activated.",status_code=400)

    old_values = { "must_set_password": user.must_set_password, "is_active": user.is_active }
    try:
        user.set_password(password)
        user.must_set_password = False
        user.is_active = True

        db.session.delete(activation_token)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    new_values = { "must_set_password": user.must_set_password, "is_active": user.is_active }

    log_entity_action(action="ACTIVATE_ACCOUNT",user=user,entity_name="User",entity_id=user.id,old_values=old_values,new_values=new_values)

    return success_response(message="Account activated successfully.", data=serialize_user(user), status_code=200)

