from typing import Any
from app.models.reservation import Reservation


def serialize_reservation(res: Reservation) -> dict[str, Any]:
    return {
        "id": str(res.id),

        "user_id": str(res.user_id),
        "user": {
            "id": str(res.user.id),
            "name": f"{res.user.first_name} {res.user.last_name}",
            "email": res.user.email
        },

        "car_id": str(res.car_id),
        "car": {
            "id": str(res.car.id),
            "brand": res.car.brand.name,
            "model": res.car.model.name,
            "license_plate": res.car.license_plate
        },

        "start_date": res.start_date.isoformat(),
        "end_date": res.end_date.isoformat(),

        "total_price": str(res.total_price),

        "status": res.status,

        "created_at": res.created_at.isoformat(),
        "updated_at": res.updated_at.isoformat()
    }


def serialize_reservations(reservations: list[Reservation]) -> list[dict[str, Any]]:
    return [serialize_reservation(res) for res in reservations]