from datetime import date
from app.models.reservation import Reservation


def get_reservation_by_user(user_id: str) -> list[Reservation]:
    return Reservation.query.filter_by(user_id=user_id).all()


def get_active_reservation_by_car(car_id: str) -> Reservation | None:
    return Reservation.query.filter_by(car_id=car_id,status="Active").first()

def get_all_reservations() -> list[Reservation]:
    return Reservation.query.order_by(Reservation.created_at.desc()).all()

def get_reservation_by_id(reservation_id: str) -> Reservation | None:
    return Reservation.query.filter_by(id=reservation_id).first()


def get_pending_or_active_reservation_by_user(user_id: str) -> Reservation | None:
    return (Reservation.query.filter(
        Reservation.user_id == user_id, Reservation.status.in_(["Pending", "Confirmed", "Active"])
    ).first())


def get_overlapping_reservation_by_car(car_id: str, start_date: date, end_date: date) -> Reservation | None:
    return Reservation.query.filter(
        Reservation.car_id == car_id,
        Reservation.status.in_(["Pending", "Confirmed", "Active"]),
        Reservation.start_date < end_date,
        Reservation.end_date > start_date
    ).first()

def get_other_overlapping_reservation_by_car(car_id: str,reservation_id: str,start_date: date,end_date: date) -> Reservation | None:
    return Reservation.query.filter(
        Reservation.car_id == car_id,
        Reservation.id != reservation_id,
        Reservation.status.in_(["Pending", "Confirmed", "Active"]),
        Reservation.start_date < end_date,
        Reservation.end_date > start_date
    ).first()
