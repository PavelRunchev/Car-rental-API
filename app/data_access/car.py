from app.extensions import db
from app.utils.database import commit
from app.models.car import Car


def get_car_by_id(car_id: str) -> Car | None:
    return db.session.get(Car, car_id)


def get_cars() -> list[Car]:
    return Car.query.order_by(Car.created_at.desc()).all()


def get_car_by_license_plate(license_plate: str) -> Car | None:
    return Car.query.filter_by(license_plate=license_plate).first()


def save_car(car: Car) -> Car:
    db.session.add(car)
    commit()
    return car


def update_car_in_db(car: Car) -> Car:
    commit()
    return car


def delete_car_from_db(car: Car) -> None:
    db.session.delete(car)


    