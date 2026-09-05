from flask import Blueprint, request
from typing import Any
from app.services import brand_service
from flask_jwt_extended import jwt_required
from app.decorators.admin_required import admin_required

brand_bp = Blueprint("brand", __name__, url_prefix="/api/brands")


@brand_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_brand():
    data: dict[str, Any] = request.get_json()
    return brand_service.create_brand(data)


@brand_bp.route("", methods=["GET"])
def get_all_brands():
    return brand_service.get_all_brands()


@brand_bp.route("/<string:brand_id>", methods=["GET"])
def get_brand(brand_id: str):
    return brand_service.get_brand(brand_id)

