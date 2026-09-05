from flask import Blueprint, Response
from app.services.fuel_type_service import get_all_fuel_types,get_fuel_type


fuel_type_bp = Blueprint("fuel_types",__name__, url_prefix="/api/fuel-types")


@fuel_type_bp.route("", methods=["GET"])
def get_fuel_types_controller() -> tuple[Response, int]:
    return get_all_fuel_types()


@fuel_type_bp.route("/<fuel_type_id>", methods=["GET"])
def get_fuel_type_controller(fuel_type_id: str) -> tuple[Response, int]:
    return get_fuel_type(fuel_type_id)