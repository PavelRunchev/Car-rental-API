from app.models.user import User
from app.extensions import db
from app.utils.database import commit
from flask import Response


from app.utils.responses import error_response, success_response
from app.utils.validators import is_valid_uuid, is_valid_email
from app.data_access.reservation import get_reservation_by_id
from app.services.email_service import send_account_activation_email
from app.services.activation_token_service import create_activation_token, delete_activation_tokens_by_user


def get_user_by_email(email: str) -> User | None:
    return User.query.filter_by(email=email).first()


def create_user(user: User) -> User | None:
    db.session.add(user)
    commit()
    return user


def get_user_by_id(user_id) -> User | None:
    return db.session.get(User, user_id)



def change_user_email_and_send_activation(reservation_id: str,new_email: str) -> tuple[Response, int]:
    if not is_valid_uuid(reservation_id):
        return error_response(message="Invalid reservation id.",status_code=400)

    reservation = get_reservation_by_id(reservation_id)
    if not reservation:
        return error_response(message="Reservation not found.",status_code=404)

    user = reservation.user
    if not user:
        return error_response(message="User not found.",status_code=404)

    if not is_valid_email(new_email):
        return error_response(message="Invalid email address.",status_code=400)

    existing_user = get_user_by_email(new_email)
    if existing_user and existing_user.id != user.id:
        return error_response(message="Email address is already in use.",status_code=409)

    delete_activation_tokens_by_user(user.id)

    user.email = new_email
    new_token = create_activation_token(user)


    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    email_sent = True
    try:
        send_account_activation_email(user=user,token=new_token,reservation=reservation)
    except Exception:
        email_sent = False
        print("Failed to send activation email.")

    if not email_sent:
        return success_response(message="User email updated, but activation email could not be sent.",status_code=200)

    return success_response(message="User email updated and activation email sent successfully.",status_code=200)