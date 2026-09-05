
from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from app.services import profile_service

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("", methods=["GET"])
@jwt_required()
def get_profile() -> tuple[Response, int]:
    return profile_service.get_profile()


@profile_bp.route("", methods=["PUT"])
@jwt_required()
def update_profile() -> tuple[Response, int]:
    return profile_service.update_profile(request.get_json())

@profile_bp.route("/email", methods=["PUT"])
@jwt_required()
def update_email() -> tuple[Response, int]:
    return profile_service.update_email(request.get_json())

@profile_bp.route("/password", methods=["PUT"])
@jwt_required()
def update_password() -> tuple[Response, int]:
    return profile_service.update_password(request.get_json())



