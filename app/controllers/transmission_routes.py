from flask import Blueprint, Response
from app.services.transmission_service import get_all_transmissions, get_transmission

transmission_bp = Blueprint("transmissions",__name__,url_prefix="/api/transmissions")


@transmission_bp.route("", methods=["GET"])
def get_transmissions_controller() -> tuple[Response, int]:
    return get_all_transmissions()


@transmission_bp.route("/<transmission_id>", methods=["GET"])
def get_transmission_controller(transmission_id: str) -> tuple[Response, int]:
    return get_transmission(transmission_id)

