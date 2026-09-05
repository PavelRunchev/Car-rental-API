from app.extensions import db
from app.models.fuel_type import FuelType
from app.utils.validators import is_valid_uuid

def get_fuel_types() -> list[FuelType]:
    return FuelType.query.order_by(FuelType.name.asc()).all()


def get_fuel_type_by_id(fuel_type_id: str) -> FuelType | None:
    if not is_valid_uuid(fuel_type_id):
        return None

    return db.session.get(FuelType,fuel_type_id)

