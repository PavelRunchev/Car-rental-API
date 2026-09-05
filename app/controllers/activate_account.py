from flask import Blueprint, request
from app.services.auth_service import activate_account


activate_account_bp = Blueprint("activate_account",__name__,url_prefix="/api/auth")


@activate_account_bp.route("/activate", methods=["POST"])
def activate_account_route():
    return activate_account(request.get_json())