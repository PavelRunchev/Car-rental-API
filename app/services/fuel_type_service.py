from flask import Response

from app.models.fuel_type import FuelType
from app.data_access.fuel_type import get_fuel_types,get_fuel_type_by_id
from app.schemas.fuel_type_schema import serialize_fuel_type,serialize_fuel_types
from app.utils.responses import error_response, success_response
from app.utils.validators import is_valid_uuid


def get_all_fuel_types() -> tuple[Response, int]:
    fuel_types: list[FuelType] = get_fuel_types()
    return success_response(data=serialize_fuel_types(fuel_types),status_code=200)


def get_fuel_type(fuel_type_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(fuel_type_id):
        return error_response(message="Invalid fuel type id.",status_code=400)

    fuel_type: FuelType | None = get_fuel_type_by_id(fuel_type_id)
    if not fuel_type:
        return error_response(message="Fuel type not found.",status_code=404)

    return success_response(data=serialize_fuel_type(fuel_type),status_code=200)