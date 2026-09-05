from typing import Any

from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from app.decorators.admin_required import admin_required
from app.services.category_service import (
    create_category,
    get_all_categories,
    get_category,
    update_category,
    delete_category,
)

category_bp = Blueprint("categories",__name__,url_prefix="/api/categories")


@category_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_category_controller() -> tuple[Response, int]:
    data: dict[str, Any] = request.get_json()
    return create_category(data)


@category_bp.route("", methods=["GET"])
def get_categories_controller() -> tuple[Response, int]:
    return get_all_categories()


@category_bp.route("/<category_id>", methods=["GET"])
def get_category_controller(category_id: str) -> tuple[Response, int]:
    return get_category(category_id)


@category_bp.route("/<category_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_category_controller(category_id: str) -> tuple[Response, int]:
    data: dict[str, Any] = request.get_json()
    return update_category(category_id, data)


@category_bp.route("/<category_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_category_controller(category_id: str) -> tuple[Response, int]:
    return delete_category(category_id)