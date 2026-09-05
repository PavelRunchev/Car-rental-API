from typing import Any
from app.models.car import Car
from app.schemas.car_image_schema import serialize_car_images


def serialize_car(car: Car) -> dict[str, Any]:
    return {
        "id": str(car.id),
        "brand_id": str(car.brand_id),
        "brand": { "id": str(car.brand.id), "name": car.brand.name },
        "category_id": str(car.category_id),
        "category": { "id": str(car.category.id), "name": car.category.name },
        "fuel_type_id": str(car.fuel_type_id),
        "fuel_type": { "id": str(car.fuel_type.id), "name": car.fuel_type.name },
        "transmission_id": str(car.transmission_id),
        "transmission": { "id": str(car.transmission.id), "name": car.transmission.name },
        "model_id": str(car.model_id),
        "model": { "id": str(car.model.id), "name": car.model.name },
        "license_plate": car.license_plate,
        "year": car.year,
        "color": car.color,
        "price_per_day": str(car.price_per_day),
        "horse_power": car.horse_power,
        "seats": car.seats,
        "doors": car.doors,
        "images": serialize_car_images(car.images),
        "description": car.description,
        "status": car.status,
        "created_at": car.created_at.isoformat(),
        "updated_at": car.updated_at.isoformat()
    }


def serialize_cars(cars: list[Car]) -> list[dict[str, Any]]:
    return [serialize_car(car) for car in cars]