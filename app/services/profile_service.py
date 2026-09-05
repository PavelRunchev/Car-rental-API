from typing import Any
from flask import Response
from flask_jwt_extended import get_jwt_identity

from app.services.user_service import get_user_by_id
from app.schemas.user_schema import serialize_user
from app.utils.responses import success_response, error_response
from app.utils.database import commit
from app.models.user import User
from app.utils.validators import validate_profile_update, validate_email_update, validate_password_update
from app.utils.normalize import normalize_name, normalize_phone, normalize_email
from app.services.user_service import get_user_by_email
from app.services.refresh_token_service import delete_user_refresh_tokens
from app.services.audit_log_service import log_entity_action

def get_profile() -> tuple[Response, int]:
    user_id: str = get_jwt_identity()

    user: User | None = get_user_by_id(user_id)

    if not user:
        return error_response(message="User not found.",status_code=404)

    return success_response(message="Profile retrieved successfully.",data=serialize_user(user))


def update_profile(data: dict[str, Any]) -> tuple[Response, int]:
    errors = validate_profile_update(data)

    if errors:
        return error_response( message="Validation failed.", status_code=400, errors=errors )

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if not user:
        return error_response( message="User not found.", status_code=404 )

    #Store current values
    old_values = { "first_name": user.first_name, "last_name": user.last_name, "phone": user.phone }

    #update user with new values
    user.first_name = normalize_name(data["first_name"])
    user.last_name = normalize_name(data["last_name"])
    user.phone = normalize_phone(data["phone"])

    #save changed to the DB
    commit()

    #get updated values
    new_values = { "first_name": user.first_name, "last_name": user.last_name, "phone": user.phone }

    log_entity_action(action="UPDATE_PROFILE",user=user,old_values=old_values,new_values=new_values)

    return success_response( message="Profile updated successfully.", data=serialize_user(user) )


def update_email(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_email_update(data)

    if errors:
        return error_response( message="Validation failed.", status_code=400, errors=errors )

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if not user:
        return error_response( message="User not found.", status_code=404 )

    email: str = normalize_email(data["email"])
    if user.email == email:
        return error_response( message="New email must be different from the current email.", status_code=400 )

    existing_user: User | None = get_user_by_email(email)

    if existing_user:
        return error_response(message="Email is already in use.",status_code=409)

    # Store current value
    old_values = { "email": user.email }
    # Update user
    user.email = email
    # Save changes
    commit()
    # Store updated value
    new_values = { "email": user.email }

    log_entity_action(action="UPDATE_EMAIL",user=user,old_values=old_values,new_values=new_values)

    return success_response( message="Email updated successfully.", data=serialize_user(user) )


def update_password(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_password_update(data)

    if errors:
        return error_response( message="Validation failed.", status_code=400,errors=errors )

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if not user:
        return error_response( message="User not found.", status_code=404 )

    current_password: str = data["current_password"]
    new_password: str = data["new_password"]
    confirm_password: str = data["confirm_password"]

    if not user.check_password(current_password):
        return error_response( message="Current password is incorrect.", status_code=401 )

    if user.check_password(new_password):
        return error_response( message="New password must be different from the current password.", status_code=400 )

    if new_password != confirm_password:
        return error_response( message="Passwords do not match.",status_code=400 )

    # Store current value
    old_values = { "password": "***" }
    # Update password
    user.set_password(new_password)
    # Save changes
    commit()
    # Invalidate all active sessions
    delete_user_refresh_tokens(user.id)
    # Store updated value
    new_values = { "password": "***" }

    log_entity_action(action="UPDATE_PASSWORD",user=user,old_values=old_values,new_values=new_values)

    return success_response(message="Password updated successfully.")