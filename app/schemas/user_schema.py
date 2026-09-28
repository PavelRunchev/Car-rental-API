from app.models.user import User
from typing import Any
from app.services.cloudinary_service import get_cloudinary_user_avatar_url

def serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "avatar_public_id": user.avatar_public_id,
        "avatar_url": get_cloudinary_user_avatar_url(user.avatar_public_id),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }
