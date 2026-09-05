from flask import Blueprint
from typing import Any
from flask import request, Response
from flask_jwt_extended import jwt_required
from app.decorators.admin_required import admin_required
from app.services.model_service import create_model, get_all_models, get_model, delete_model, update_model

model_bp = Blueprint("models",__name__, url_prefix="/api/models")


@model_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_model_controller() -> tuple[Response, int]:
    data: dict[str, Any] = request.get_json()
    return create_model(data)


@model_bp.route("", methods=["GET"])
def get_models_controller() -> tuple[Response, int]:
    return get_all_models()


@model_bp.route("/<model_id>", methods=["GET"])
def get_model_controller(model_id: str) -> tuple[Response, int]:
    return get_model(model_id)


@model_bp.route("/<model_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_model_controller(model_id: str) -> tuple[Response, int]:
    return delete_model(model_id)


@model_bp.route("/<model_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_model_controller(model_id: str) -> tuple[Response, int]:
    data: dict[str, Any] = request.get_json()
    return update_model(model_id, data)