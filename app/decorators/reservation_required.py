from functools import wraps
from flask_jwt_extended import get_jwt_identity

from app.models.user import User
from app.services.user_service import get_user_by_id
from app.utils.responses import error_response


def reservation_access_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        requested_user_id: str = kwargs.get("user_id")
        user: User = get_user_by_id(get_jwt_identity())

        if not user:
            return error_response(message="User not found.",status_code=404)

        if user.role in {"Admin", "Operator"}:
            return func(*args, **kwargs)

        if user.role == "User" and str(user.id) == str(requested_user_id):
            return func(*args, **kwargs)

        return error_response(message="You do not have permission to access these reservations.",status_code=403)

    return wrapper