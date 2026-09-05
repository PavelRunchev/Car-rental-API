from app.models.transmission import Transmission
from app.extensions import db
from app.utils.validators import is_valid_uuid

def get_transmissions() -> list[Transmission]:
    return Transmission.query.order_by(Transmission.name.asc()).all()


def get_transmission_by_id(transmission_id: str) -> Transmission | None:
    if not is_valid_uuid(transmission_id):
        return None

    return db.session.get(Transmission,transmission_id)

