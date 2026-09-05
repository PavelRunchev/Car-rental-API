from typing import Any
from app.models.transmission import Transmission


def serialize_transmission(transmission: Transmission) -> dict[str, Any]:
    return {
        "id": str(transmission.id),
        "name": transmission.name,
        "created_at": transmission.created_at.isoformat(),
        "updated_at": transmission.updated_at.isoformat()
    }


def serialize_transmissions(transmissions: list[Transmission]) -> list[dict[str, Any]]:
    return [serialize_transmission(transmission) for transmission in transmissions]


