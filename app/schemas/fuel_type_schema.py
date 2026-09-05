from typing import Any
from app.models.fuel_type import FuelType


def serialize_fuel_type(fuel_type: FuelType) -> dict[str, Any]:
    return {
        "id": str(fuel_type.id),
        "name": fuel_type.name,
        "created_at": fuel_type.created_at.isoformat(),
        "updated_at": fuel_type.updated_at.isoformat()
    }


def serialize_fuel_types(
    fuel_types: list[FuelType]) -> list[dict[str, Any]]:
    return [serialize_fuel_type(fuel_type) for fuel_type in fuel_types]

