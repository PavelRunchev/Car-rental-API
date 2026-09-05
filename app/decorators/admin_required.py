from functools import wraps

from flask_jwt_extended import get_jwt_identity
from app.services.user_service import get_user_by_id
from app.utils.responses import error_response
from app.models.user import User


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id: str = get_jwt_identity()
        user: User | None = get_user_by_id(user_id)

        if not user:
            return error_response(message="User not found.",status_code=404)

        if user.role != "Admin":
            return error_response(message="Administrator privileges are required.",status_code=403,)

        return func(*args, **kwargs)

    return wrapper

