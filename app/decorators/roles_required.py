from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.services.user_service import get_user_by_id
from app.utils.responses import error_response


def roles_required(*allowed_roles: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id: str = get_jwt_identity()
            user = get_user_by_id(user_id)

            if not user:
                return error_response(message="User not found.",status_code=404)

            if user.role not in allowed_roles:
                return error_response(message="You do not have permission to perform this action.",status_code=403)

            return func(*args, **kwargs)

        return wrapper

    return decorator