from typing import Any
from datetime import datetime
from uuid import uuid4
from flask import Response

from app.extensions import db
from flask_jwt_extended import get_jwt_identity

from app.models.user import User
from app.models.car import Car
from app.models.reservation import Reservation
from app.models.payment import Payment

from app.utils.responses import error_response, success_response
from app.services.audit_log_service import log_entity_action
from app.utils.validators import validate_reservation, is_valid_uuid, validate_operator_user
from app.services.user_service import get_user_by_id
from app.data_access.car import get_car_by_id
from app.schemas.reservation_schema import serialize_reservation
from app.data_access.reservation import (
    get_reservation_by_user,
    get_active_reservation_by_car,
    get_all_reservations,
    get_reservation_by_id,
    get_overlapping_reservation_by_car,
    get_pending_or_active_reservation_by_user,
    get_other_overlapping_reservation_by_car
)
from app.services.email_service import send_account_activation_email
from app.services.activation_token_service import create_activation_token
from app.utils.normalize import normalize_email, normalize_name, normalize_phone
from app.services.user_service import get_user_by_email
from app.services.payment_service import create_payment_intent


def create_reservation(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_reservation(data)

    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if not user:
        return error_response(message="Customer not found.",status_code=404)

    if not user.is_active:
        return error_response(message="Customer is inactive.",status_code=403)

    car: Car | None = get_car_by_id(data["car_id"])
    if not car:
        return error_response(message="Car not found.",status_code=404)

    if car.status != "Available":
        return error_response(message="Car is not available.",status_code=409)

    start_date = datetime.strptime(data["start_date"],"%Y-%m-%d").date()
    end_date = datetime.strptime(data["end_date"],"%Y-%m-%d").date()

    # Check if car is already reserved during this period
    existing_car_reservation: Reservation | None = get_overlapping_reservation_by_car(car.id, start_date, end_date)
    if existing_car_reservation:
        return error_response(message="Car is already reserved for the selected dates.", status_code=409)

    # Check if user already has a pending/active reservation
    existing_user_reservation: Reservation | None = get_pending_or_active_reservation_by_user(user.id)
    if existing_user_reservation:
        return error_response(message="User already has a pending, confirmed, or active reservation.",status_code=409)


    days: int = (end_date - start_date).days
    total_price = days * car.price_per_day

    reservation = Reservation(
        id=uuid4(),
        user_id=user.id,
        car_id=car.id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status="Pending"
    )

    try:
        db.session.add(reservation)
        db.session.flush()

        payment_intent = create_payment_intent(
            amount=int(total_price * 100),
            currency="eur",
            metadata={ "reservation_id": str(reservation.id),"user_id": str(user.id) }
        )

        payment = Payment(
            reservation_id=reservation.id,
            user_id=user.id,
            amount=total_price,
            currency="EUR",
            status="Pending",
            payment_method="Online",
            provider="Stripe",
            provider_payment_id=payment_intent.id
        )

        db.session.add(payment)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    log_entity_action(
        action="CREATE_RESERVATION",
        user=user,
        entity_name="Reservation",
        entity_id=reservation.id,
        new_values={
            "car_id": str(car.id),
            "license_plate": car.license_plate,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_price": str(total_price),
            "status": reservation.status,
            "payment_status": payment.status,
            "payment_provider": payment.provider,
            "provider_payment_id": payment.provider_payment_id,
            "payment_method": payment.payment_method
        }
    )

    return success_response(
        message="Reservation created successfully.",
        data= {
            "reservation": serialize_reservation(reservation),
            "payment": {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret
            }
        },
        status_code=201
    )


def create_operator_reservation(data: dict[str, Any]) -> tuple[Response, int]:
    user_data: dict[str, Any] = data.get("user", {})
    reservation_data: dict[str, Any] = data.get("reservation", {})

    user_errors = validate_operator_user(user_data)
    if user_errors:
        return error_response(message="Customer registration validation failed.",status_code=400,errors=user_errors)

    reservation_errors = validate_reservation(reservation_data)
    if reservation_errors:
        return error_response(message="Validation failed.",status_code=400,errors=reservation_errors)


    # Operator/Admin who performs the action
    operator: User | None = get_user_by_id(get_jwt_identity())
    if not operator:
        return error_response( message="User not found.", status_code=404)

    if not operator.is_active:
        return error_response(message="User is inactive.",status_code=403)

    if operator.role not in {"Admin", "Operator"}:
        return error_response(message="Operator or administrator privileges are required.",status_code=403)

    first_name = normalize_name(user_data["first_name"])
    last_name = normalize_name(user_data["last_name"])
    email = normalize_email(user_data["email"])
    phone = normalize_phone(user_data["phone"])

    existing_user = get_user_by_email(email)
    if existing_user:
        return error_response(message="Email already exists.",status_code=409)


    car: Car | None = get_car_by_id(reservation_data["car_id"])
    if not car:
        return error_response(message="Car not found.", status_code=404)

    if car.status != "Available":
        return error_response(message="Car is not available.",status_code=409)


    start_date = None
    end_date = None
    try:
        start_date = datetime.strptime(reservation_data["start_date"],"%Y-%m-%d").date()
        end_date = datetime.strptime(reservation_data["end_date"],"%Y-%m-%d").date()
    except ValueError:
        return error_response(message="Invalid date format. Expected YYYY-MM-DD.",status_code=400)


    if end_date <= start_date:
        return error_response(message="End date must be after start date.",status_code=400)

    # Check car is reserved this period of date.
    overlapping_reservation: Reservation | None = get_overlapping_reservation_by_car(car.id, start_date, end_date)
    if overlapping_reservation:
        return error_response(message="Car is already reserved for the selected dates.",status_code=409)

    # We don't check for a user whether they have reservations because they are registering now!!!


    # Calculate reservation price
    days: int = (end_date - start_date).days
    total_price = days * car.price_per_day

    # Create Customer
    user = User(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=None,
        must_set_password=True,
        role="User",
        is_active=False
    )

    # Create reservation
    reservation = Reservation(
        id=uuid4(),
        user_id=user.id,
        car_id=car.id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status="Pending"
    )

    payment = Payment(
        reservation_id=reservation.id,
        user_id=user.id,
        amount=total_price,
        currency="EUR",
        status="Pending",
        payment_method="Terminal",
        provider="Stripe"
    )

    # Create active token
    activate_token: str | None = None
    try:
        activate_token = create_activation_token(user)

        db.session.add(user)
        db.session.add(reservation)
        db.session.add(payment)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


    if user.must_set_password and activate_token:
        try:
            send_account_activation_email(user=user,token=activate_token,reservation=reservation)
        except Exception:
            print("Failed to send account activation email.")


    log_entity_action(
        action="CREATE_RESERVATION",
        user=operator,
        entity_name="Reservation",
        entity_id=reservation.id,
        new_values={
            "user_id": str(user.id),
            "user_name": f"{user.first_name} {user.last_name}",
            "user_email": user.email,
            "car_id": str(car.id),
            "license_plate": car.license_plate,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_price": str(total_price),
            "status": reservation.status,
            "payment_status": payment.status,
            "payment_method": payment.payment_method,
            "payment_provider": payment.provider,
            "payment_id": str(payment.id),
            "created_by": str(operator.id),
            "created_by_role": operator.role
        }
    )

    return success_response( message="Reservation created successfully.", data=serialize_reservation(reservation), status_code=201)


def activate_reservation(reservation_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(reservation_id):
        return error_response(message="Invalid reservation id.",status_code=400)

    reservation: Reservation | None = get_reservation_by_id(reservation_id)
    if not reservation:
        return error_response(message="Reservation not found.",status_code=404)


    operator: User | None = get_user_by_id(get_jwt_identity())
    if not operator:
        return error_response(message="User not found.",status_code=404)

    if not operator.is_active:
        return error_response(message="User is inactive.",status_code=403)

    if operator.role not in {"Admin", "Operator"}:
        return error_response(message="Operator privileges are required.",status_code=403)


    if reservation.status != "Confirmed":
        return error_response(message="Only confirmed reservations can be activated.",status_code=409)

    car: Car | None = reservation.car
    if not car:
        return error_response(message="Car not found.",status_code=404)

    if car.status != "Available":
        return error_response( message="Car is not available.", status_code=409)

    old_values = {"status": reservation.status, "car_status": car.status }

    reservation.status = "Active"
    car.status = "Reserved"

    new_values = { "status": reservation.status, "car_status": car.status }

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    log_entity_action(action="ACTIVATE_RESERVATION",user=operator, entity_name="Reservation", entity_id=reservation.id, old_values=old_values, new_values=new_values )

    return success_response( message="Reservation activated successfully.", data=serialize_reservation(reservation), status_code=200)


def complete_reservation(reservation_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(reservation_id):
        return error_response(message="Invalid reservation id.",status_code=400)

    reservation: Reservation | None = get_reservation_by_id(reservation_id)
    if not reservation:
        return error_response(message="Reservation not found.",status_code=404)

    operator: User | None = get_user_by_id(get_jwt_identity())
    if not operator:
        return error_response(message="Operator not found.",status_code=404)

    if not operator.is_active:
        return error_response(message="Operator is inactive.",status_code=403)

    if operator.role not in {"Admin", "Operator"}:
        return error_response(message="Operator privileges are required.",status_code=403)


    if reservation.status != "Active":
        return error_response(message="Only active reservations can be completed.",status_code=409)

    car: Car | None = reservation.car
    if not car:
        return error_response( message="Car not found.", status_code=404)

    old_values = {"status": reservation.status,"car_status": car.status}

    reservation.status = "Completed"
    car.status = "Available"

    new_values = {"status": reservation.status,"car_status": car.status}

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    log_entity_action(action="COMPLETE_RESERVATION", user=operator,entity_name="Reservation",entity_id=reservation.id,old_values=old_values,new_values=new_values)

    return success_response(message="Reservation completed successfully.",data=serialize_reservation(reservation),status_code=200)



def update_reservation(reservation_id: str, data: dict[str, Any]) -> tuple[Response, int]:
        if not is_valid_uuid(reservation_id):
            return error_response(message="Invalid reservation id.",status_code=400)

        reservation: Reservation | None = get_reservation_by_id(reservation_id)
        if not reservation:
            return error_response(message="Reservation not found.",status_code=404)

        admin: User | None = get_user_by_id(get_jwt_identity())
        if not admin:
            return error_response(message="Admin not found.",status_code=404)

        if not admin.is_active:
            return error_response(message="Admin is inactive.",status_code=403)

        if admin.role != "Admin":
            return error_response(message="Administrator privileges are required.",status_code=403)

        new_status = data.get("status")

        if reservation.status == new_status:
            return error_response(message="Reservation already has this status.",status_code=409)

        allowed_statuses = {"Pending","Confirmed","Active","Completed","Cancelled"}
        if new_status not in allowed_statuses:
            return error_response(message="Invalid reservation status.",status_code=400)


        car: Car | None = reservation.car
        if not car:
            return error_response(message="Car not found.",status_code=404)

        old_values = { "status": reservation.status, "car_id": str(car.id), "license_plate": car.license_plate, "car_status": car.status }

        reservation.status = new_status
        if new_status == "Active":
            overlapping_reservation = get_other_overlapping_reservation_by_car(car.id,reservation.id,reservation.start_date,reservation.end_date)

            if overlapping_reservation:
                return error_response(message="Car is already reserved for the selected dates.",status_code=409)

            car.status = "Reserved"
        else:
            car.status = "Available"

        new_values = { "status": reservation.status,"car_id": str(car.id),"license_plate": car.license_plate,  "car_status": car.status }

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        log_entity_action(action="UPDATE_RESERVATION", user=admin, entity_name="Reservation",
            entity_id=reservation.id, old_values=old_values, new_values=new_values
        )

        return success_response(message="Reservation updated successfully.",data=serialize_reservation(reservation),status_code=200)


def get_reservations() -> tuple[Response, int]:
    reservations: list[Reservation] = get_all_reservations()

    return success_response(message="Reservations retrieved successfully.",
        data=[serialize_reservation(res) for res in reservations], status_code=200
    )


def get_reservation(reservation_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(reservation_id):
        return error_response(message="Invalid reservation id.",status_code=400)

    reservation: Reservation | None = get_reservation_by_id(reservation_id)

    if not reservation:
        return error_response(message="Reservation not found.",status_code=404)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)
    if user.role == "User" and reservation.user_id != user.id:
        return error_response(message="You do not have permission to view this reservation.",status_code=403)

    return success_response(
        message="Reservation retrieved successfully.",
        data=serialize_reservation(reservation),
        status_code=200
    )


def get_user_reservation(user_id: str) -> tuple[Response, int]:

    print(user_id)
    if not is_valid_uuid(user_id):
        return error_response(message="Invalid user id.",status_code=400)

    reservations: list[Reservation] = get_reservation_by_user(user_id)
    return success_response(message="Reservations retrieved successfully.", data=[serialize_reservation(res) for res in reservations], status_code=200)


def get_car_reservation(car_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(car_id):
        return error_response(message="Invalid car id.",status_code=400)

    reservations: list[Reservation] = get_active_reservation_by_car(car_id)
    return success_response(message="Car reservations retrieved successfully.",data=[serialize_reservation(res) for res in reservations],status_code=200)