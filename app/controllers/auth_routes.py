from flask import Blueprint, request, Response
from app.services import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple[Response, int]:
    return auth_service.register(request.get_json())


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    return auth_service.login(request.get_json())

@auth_bp.route("/refresh", methods=["POST"])
def refresh() -> tuple[Response, int]:
    return auth_service.refresh(request.get_json())

@auth_bp.route("/logout", methods=["POST"])
def logout() -> tuple[Response, int]:
    return auth_service.logout(request.get_json())
