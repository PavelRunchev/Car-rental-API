import stripe
from app.extensions import db
from flask import Response, current_app, request
from flask_jwt_extended import get_jwt_identity
from app.utils.responses import error_response, success_response
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.data_access.reservation import get_reservation_by_id
from app.utils.validators import is_valid_uuid
from app.services.audit_log_service import log_entity_action
from app.models.user import User
from app.services.user_service import get_user_by_id


def create_test_payment() -> tuple[Response, int]:
    try:
        payment_intent = stripe.PaymentIntent.create(amount=15000, currency="eur",payment_method_types=["card"])

        return success_response(
            message="PaymentIntent created successfully.",
            data={
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status
            },
            status_code=201
        )

    except stripe.StripeError as e:
        return error_response(message=str(e),status_code=400)


def create_payment_intent(amount: int, currency: str = "EUR", metadata: dict[str, str] | None = None):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        payment_method_types=["card"],
        metadata=metadata or {}
    )

def create_terminal_payment_intent(amount: int,currency: str = "EUR",metadata: dict[str, str] | None = None):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        payment_method_types=["card_present"],
        metadata=metadata or {}
    )


def handle_stripe_webhook() -> tuple[Response, int]:
    payload = request.get_data()
    signature = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            current_app.config["STRIPE_WEBHOOK_SECRET"]
        )

    except ValueError:
        return error_response(message="Invalid webhook payload.",status_code=400)

    except stripe.SignatureVerificationError:
        return error_response(message="Invalid webhook signature.",status_code=400)

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        payment: Payment | None = Payment.query.filter_by(provider_payment_id=payment_intent_id).first()
        if not payment:
            return error_response(message="Payment not found.", status_code=404)

        reservation: Reservation | None = payment.reservation
        if not reservation:
            return error_response(message="Reservation not found.")

        if payment.status == "Paid":
            return success_response(message="Payment already processed.", status_code=200)

        payment.status = "Paid"
        reservation.status = "Confirmed"

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print(f"Payment succeeded!  PaymentIntent: {payment_intent_id}")
        print(f"Payment: {payment.id}, Reservation: {reservation.id}")

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        payment: Payment | None = Payment.query.filter_by(provider_payment_id=payment_intent_id).first()
        if not payment:
            return error_response(message="Payment not found.",status_code=404)

        if payment.status == "Failed":
            return success_response(message="Payment failure already processed.",status_code=200)

        payment.status = "Failed"

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print("Payment failed!")
        print(f"PaymentIntent: {payment_intent_id}")

    elif event["type"] == "terminal.reader.action_succeeded":
        print("Terminal reader action succeeded.")

    elif event["type"] == "terminal.reader.action_failed":
        reader = event["data"]["object"]
        action = reader.get("action", {})

        process_payment_intent = action.get("process_payment_intent", {})
        payment_intent_id = process_payment_intent.get("payment_intent")

        failure_code = action.get("failure_code")
        failure_message = action.get("failure_message")

        if not payment_intent_id:
            print("Terminal payment failed, but PaymentIntent was not found.")
            print(f"Failure code: {failure_code}")
            print(f"Failure message: {failure_message}")
            return success_response(message="Terminal reader action failed without PaymentIntent.",status_code=200)

        payment: Payment | None = Payment.query.filter_by(provider_payment_id=payment_intent_id).first()
        if not payment:
            return error_response(message="Payment not found.",status_code=404)

        if payment.status == "Failed":
            return success_response(message="Payment failure already processed.",status_code=200)

        try:
            payment.status = "Failed"
            db.session.commit()

            print("Terminal payment failed.")
            print(f"PaymentIntent: {payment_intent_id}")
            print(f"Failure code: {failure_code}")
            print(f"Failure message: {failure_message}")

        except Exception:
            db.session.rollback()

            print("Terminal payment rollback.")
            print(f"PaymentIntent: {payment_intent_id}")

            raise


    return success_response( message="Webhook received successfully.", status_code=200 )



def create_terminal_payment(reservation_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(reservation_id):
        return error_response( message="Invalid reservation id.", status_code=400 )

    reservation: Reservation | None = get_reservation_by_id(reservation_id)
    if not reservation:
        return error_response(message="Reservation not found.",status_code=404)

    payment: Payment | None = reservation.payment
    if not payment:
        return error_response(message="Payment not found.",status_code=404)

    if payment.payment_method != "Terminal":
        return error_response( message="Payment method must be Terminal.", status_code=409 )

    if payment.status != "Pending":
        return error_response( message="Payment is not pending.", status_code=409 )

    operator: User | None = get_user_by_id(get_jwt_identity())
    if not operator:
        return error_response(message="User not found.",status_code=404)

    if not operator.is_active:
        return error_response(message="User is inactive.",status_code=403)

    if operator.role not in {"Admin", "Operator"}:
        return error_response(message="Only Admin or Operator can start a terminal payment.",status_code=403)

    if payment.provider != "Stripe":
        return error_response(message="Unsupported payment provider.",status_code=409)

    if payment.provider_payment_id:
        return error_response(message="Terminal payment has already been started.",status_code=409)


    reader_id = current_app.config["STRIPE_TERMINAL_READER_ID"]
    if not reader_id:
        return error_response(message="Stripe Terminal reader is not configured.",status_code=500)


    try:
        payment_intent = create_terminal_payment_intent(
            amount=int(payment.amount * 100),
            currency=payment.currency.lower(),
            metadata={
                "reservation_id": str(reservation.id),
                "user_id": str(payment.user_id)
            }
        )

        reader = stripe.terminal.Reader.process_payment_intent( reader_id, payment_intent=payment_intent.id )
        payment.provider_payment_id = payment_intent.id

        db.session.commit()
    except stripe.StripeError as e:
        db.session.rollback()
        return error_response(message=str(e),status_code=400)
    except Exception:
        db.session.rollback()
        raise

    log_entity_action(
        action="CREATE_TERMINAL_PAYMENT",
        user=operator,
        entity_name="Payment",
        entity_id=payment.id,
        new_values={
            "reservation_id": str(reservation.id),
            "payment_method": payment.payment_method,
            "payment_status": payment.status,
            "payment_provider": payment.provider,
            "provider_payment_id": payment.provider_payment_id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "reader_id": reader.id
        }
    )

    return success_response(
        message="Terminal payment started successfully.",
        data={
            "payment_id": str(payment.id),
            "reservation_id": str(reservation.id),
            "payment_intent_id": payment_intent.id,
            "reader_id": reader.id,
            "reader_status": reader.status,
            "reader_action_status": (
                reader.action.status
                if reader.action
                else None
            ),
            "payment_status": payment.status
        },
        status_code=201
    )