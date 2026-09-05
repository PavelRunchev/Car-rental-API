from flask import Response

from app.models.transmission import Transmission
from app.data_access.transmission import get_transmissions,get_transmission_by_id
from app.schemas.transmission_schema import serialize_transmission, serialize_transmissions
from app.utils.responses import error_response, success_response
from app.utils.validators import is_valid_uuid


def get_all_transmissions() -> tuple[Response, int]:
    transmissions: list[Transmission] = get_transmissions()
    return success_response(data=serialize_transmissions(transmissions),status_code=200)


def get_transmission(transmission_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(transmission_id):
        return error_response(message="Invalid transmission id.",status_code=400)

    transmission: Transmission | None = get_transmission_by_id(transmission_id)

    if not transmission:
        return error_response(message="Transmission not found.",status_code=404)

    return success_response(data=serialize_transmission(transmission),status_code=200)


