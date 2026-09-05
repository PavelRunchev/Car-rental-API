from typing import Any

from app.models.category import Category


def serialize_category(category: Category) -> dict[str, Any]:
    return {
        "id": str(category.id),
        "name": category.name,
        "created_at": category.created_at.isoformat(),
        "updated_at": category.updated_at.isoformat()
    }


def serialize_categories(categories: list[Category]) -> list[dict[str, Any]]:
    return [serialize_category(category) for category in categories]