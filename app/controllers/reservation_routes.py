from typing import Any
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.decorators.roles_required import roles_required
from app.decorators.reservation_required import reservation_access_required
from app.services.user_service import change_user_email_and_send_activation
from app.utils.responses import error_response
from app.services.reservation_service import (
    create_reservation,
    update_reservation,
    get_reservations,
    get_reservation,
    get_user_reservation,
    get_car_reservation,
    activate_reservation,
    complete_reservation,
    create_operator_reservation
)

reservation_bp = Blueprint("reservation", __name__, url_prefix="/api/reservations")

@reservation_bp.route("", methods=["POST"])
@jwt_required()
@roles_required("User")
def create_reservation_route():
    return create_reservation(request.get_json())


@reservation_bp.route("/operator", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Operator")
def create_operator_reservation_route():
    return create_operator_reservation(request.get_json())


@reservation_bp.route("/<string:reservation_id>/activate",methods=["PUT"])
@jwt_required()
@roles_required("Admin", "Operator")
def activate_reservation_route(reservation_id: str):
    return activate_reservation(reservation_id)


@reservation_bp.route("/<string:reservation_id>/complete",methods=["PUT"])
@jwt_required()
@roles_required("Admin", "Operator")
def complete_reservation_route(reservation_id: str):
    return complete_reservation(reservation_id)


@reservation_bp.route("/<string:reservation_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin")
def update_reservation_route(reservation_id: str):
    return update_reservation(reservation_id,request.get_json())


@reservation_bp.route("", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_reservations_route():
    return get_reservations()


@reservation_bp.route("/<string:reservation_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_reservation_route(reservation_id: str):
    return get_reservation(reservation_id)


@reservation_bp.route("/user/<string:user_id>", methods=["GET"])
@jwt_required()
@reservation_access_required
def get_user_reservations_route(user_id: str):
    return get_user_reservation(user_id)


@reservation_bp.route("/car/<string:car_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Operator")
def get_car_reservations_route(car_id: str):
    return get_car_reservation(car_id)



@reservation_bp.route("/user/<reservation_id>/activation-email",methods=["POST"])
@jwt_required()
@roles_required("Admin", "Operator")
def resend_activation_email(reservation_id: str):
    data: dict[str, Any] = request.get_json()
    print(reservation_id, data)
    new_email: str | None = data.get("email")
    if new_email is None:
        return error_response(message="Email is required.",status_code=400)

    return change_user_email_and_send_activation( reservation_id, new_email )


