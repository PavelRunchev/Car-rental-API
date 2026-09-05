from app.models.brand import Brand
from typing import Any

def serialize_brand(brand: Brand) -> dict[str, Any]:
    return {
        "id": str(brand.id),
        "name": brand.name,
        "logo_public_id": brand.logo_public_id,
        "created_at": brand.created_at.isoformat(),
        "updated_at": brand.updated_at.isoformat(),
    }


def serialize_brands(brands: list[Brand]) -> list[dict]:
    return [serialize_brand(brand) for brand in brands]