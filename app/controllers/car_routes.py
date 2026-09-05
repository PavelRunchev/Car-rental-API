from typing import Any
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required
from werkzeug.datastructures import FileStorage
from app.services.car_service import create_car, delete_car, get_all_cars, get_car, update_car
from app.decorators.admin_required import admin_required

car_bp = Blueprint("cars",__name__,url_prefix="/api/cars")


def parse_int_fields(data: dict[str, Any], fields: list[str]) -> dict[str, Any] | None:
    for field in fields:
        if field in data:
            try:
                data[field] = int(data[field])
            except (TypeError, ValueError):
                pass
    return data

@car_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_car_controller() -> tuple[Response, int]:
    data: dict[str, Any] = request.form.to_dict()
    data: dict[str, Any] = parse_int_fields(data,["year", "horse_power", "seats", "doors"])

    images: list[FileStorage] = request.files.getlist("images")
    return create_car(data, images)


@car_bp.route("", methods=["GET"])
def get_cars_controller() -> tuple[Response, int]:
    return get_all_cars()


@car_bp.route("/<car_id>", methods=["GET"])
def get_car_controller(car_id: str) -> tuple[Response, int]:
    return get_car(car_id)


@car_bp.route("/<car_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_car_controller(car_id: str) -> tuple[Response, int]:
    data: dict[str, Any] = request.form.to_dict()
    data: dict[str, Any] = parse_int_fields(data, ["year", "horse_power", "seats", "doors"])

    images: dict[int, FileStorage] = {}
    for key, image in request.files.items():
        if key.startswith("image_") and image.filename:
            image_number = int(key.split("_")[1])
            images[image_number] = image

    return update_car(car_id, data, images)


@car_bp.route("/<car_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_car_controller(car_id: str) -> tuple[Response, int]:
    return delete_car(car_id)