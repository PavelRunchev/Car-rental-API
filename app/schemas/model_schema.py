from typing import Any
from app.models.model import Model


def serialize_model(model: Model) -> dict[str, Any]:
    return {
        "id": str(model.id),
        "name": model.name,
        "brand_id": str(model.brand_id),
        "brand": {
            "id": str(model.brand.id),
            "name": model.brand.name
        },
        "created_at": model.created_at.isoformat(),
        "updated_at": model.updated_at.isoformat()
    }


def serialize_models(models: list[Model]) -> list[dict[str, Any]]:
    return [serialize_model(model) for model in models]