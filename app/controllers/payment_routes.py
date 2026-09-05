from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from app.decorators.roles_required import roles_required
from app.services.payment_service import create_terminal_payment

from app.services.payment_service import create_test_payment, handle_stripe_webhook

payment_bp = Blueprint("payment",__name__,url_prefix="/api/payments")

@payment_bp.route("/test", methods=["POST"])
@jwt_required()
def create_test_payment_route():
    return create_test_payment()


@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook_route():
    return handle_stripe_webhook()


@payment_bp.route("/terminal/<string:reservation_id>",methods=["POST"])
@jwt_required()
@roles_required("Admin", "Operator")
def create_terminal_payment_route(reservation_id: str) -> tuple[Response, int]:
    return create_terminal_payment(reservation_id)