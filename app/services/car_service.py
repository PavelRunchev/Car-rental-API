from typing import Any
from uuid import uuid4
from flask import Response

from app.extensions import db
from flask_jwt_extended import get_jwt_identity
from werkzeug.datastructures import FileStorage

from app.models.user import User
from app.models.brand import Brand
from app.models.model import Model
from app.models.category import Category
from app.models.fuel_type import FuelType
from app.models.transmission import Transmission
from app.models.car import Car
from app.models.car_image import CarImage

from app.data_access.car import get_cars, get_car_by_id, get_car_by_license_plate, delete_car_from_db
from app.services.cloudinary_service import upload_cloudinary_car_image, delete_cloudinary_car_images, restore_cloudinary_car_image, get_cloudinary_car_image

from app.utils.responses import error_response, success_response
from app.schemas.car_schema import serialize_car, serialize_cars
from app.utils.normalize import normalize_license_plate, normalize_color
from app.services.audit_log_service import log_entity_action
from app.services.user_service import get_user_by_id
from app.data_access.brand import get_brand_by_id
from app.data_access.model import create_model
from app.data_access.category import get_category_by_id
from app.data_access.fuel_type import get_fuel_type_by_id
from app.data_access.transmission import get_transmission_by_id
from app.data_access.car_image import get_car_image_by_number
from app.utils.validators import is_valid_uuid, validate_car, validate_car_image_updates

#helper function
def get_car_dependencies(data: dict[str, Any]) -> tuple[Brand | None, Category | None, FuelType | None, Transmission | None, str | None]:
    brand = None
    category = None
    fuel_type = None
    transmission = None

    if "brand_id" in data:
        if not is_valid_uuid(data["brand_id"]):
            return None, None, None, None, "Invalid brand UUID."

        brand = get_brand_by_id(data["brand_id"])

    if "category_id" in data:
        if not is_valid_uuid(data["category_id"]):
            return None, None, None, None, "Invalid category UUID."

        category = get_category_by_id(data["category_id"])

    if "fuel_type_id" in data:
        if not is_valid_uuid(data["fuel_type_id"]):
            return None, None, None, None, "Invalid fuel type UUID."

        fuel_type = get_fuel_type_by_id(data["fuel_type_id"])

    if "transmission_id" in data:
        if not is_valid_uuid(data["transmission_id"]):
            return None, None, None, None, "Invalid transmission UUID."

        transmission = get_transmission_by_id(data["transmission_id"])

    return brand, category, fuel_type, transmission, None


#helper function
def get_car_values(brand_id, category_id, fuel_type_id, transmission_id, model_name, license_plate, year,
        color, price_per_day, horse_power, seats, doors, description, status
    ) -> dict[str, Any]:
    return {
        "brand_id": str(brand_id),
        "category_id": str(category_id),
        "fuel_type_id": str(fuel_type_id),
        "transmission_id": str(transmission_id),
        "model": model_name,
        "license_plate": license_plate,
        "year": year,
        "color": color,
        "price_per_day": str(price_per_day),
        "horse_power": horse_power,
        "seats": seats,
        "doors": doors,
        "description": description,
        "status": status
    }


def create_car(data: dict[str, Any], images: list[FileStorage]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_car(data)

    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    user: User | None = get_user_by_id(get_jwt_identity())
    if not user:
        return error_response(message="User not found.", status_code=404)

    brand, category, fuel_type, transmission, dependency_error = get_car_dependencies(data)

    if dependency_error:
        return error_response(message=dependency_error, status_code=400)

    if not brand:
        return error_response(message="Brand not found.",status_code=404)

    if not category:
        return error_response(message="Category not found.",status_code=404)

    if not fuel_type:
        return error_response( message="Fuel type not found.",status_code=404)

    if not transmission:
        return error_response( message="Transmission not found.", status_code=404)

    existing_car: Car | None = get_car_by_license_plate(normalize_license_plate(data["license_plate"]))
    if existing_car:
        return error_response(message="Car with this license plate already exists.",status_code=409)

    model: Model = create_model(name=data["model"].strip(), brand_id = brand.id)

    car: Car = Car(
        id=uuid4(),
        brand_id=brand.id,
        category_id=category.id,
        fuel_type_id=fuel_type.id,
        transmission_id=transmission.id,
        model_id=model.id,
        license_plate=normalize_license_plate(data["license_plate"]),
        year=data["year"],
        color=normalize_color(data["color"]),
        price_per_day=data["price_per_day"],
        horse_power=data["horse_power"],
        seats=data["seats"],
        doors=data["doors"],
        description=data.get("description")
    )

    uploaded_public_ids: list[str] = []
    try:
        for index, image in enumerate(images, start=1):
            public_id: str = upload_cloudinary_car_image(file=image,car_id=str(car.id),image_number=index)
            uploaded_public_ids.append(public_id)
            db.session.add(CarImage(car_id=car.id,public_id=public_id,is_primary=(index == 1)))

        db.session.add(car)
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_cloudinary_car_images(uploaded_public_ids)
        raise

    log_entity_action( action="CREATE_CAR", user=user, entity_name="Car", entity_id=car.id,
        new_values={"brand": brand.name,"model": model.name,"license_plate": car.license_plate,"year": car.year}
    )

    return success_response(message="Car created successfully.",data=serialize_car(car),status_code=201)


def get_all_cars() -> tuple[Response, int]:
    cars: list[Car] = get_cars()
    return success_response(data=serialize_cars(cars), status_code=200)


def get_car(car_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(car_id):
        return error_response(message="Invalid car id.",status_code=400)

    car: Car | None = get_car_by_id(car_id)
    if not car:
        return error_response(message="Car not found.",status_code=404)

    return success_response(data=serialize_car(car),status_code=200)


def update_car(car_id: str, data: dict[str, Any], images: dict[int, FileStorage]) -> tuple[Response, int]:
    if not is_valid_uuid(car_id):
        return error_response(message="Invalid car id.",status_code=400)

    car: Car | None = get_car_by_id(car_id)
    if not car:
        return error_response(message="Car not found.",status_code=404)


    errors: dict[str, str] = validate_car(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)


    user: User | None = get_user_by_id(get_jwt_identity())
    if not user:
        return error_response(message="User not found.",status_code=404)


    brand, category, fuel_type, transmission, dependency_error = get_car_dependencies(data)

    if dependency_error:
        return error_response(message=dependency_error, status_code=400)

    if not brand:
        return error_response(message="Brand not found.", status_code=404)
    if not category:
        return error_response(message="Category not found.", status_code=404)
    if not fuel_type:
        return error_response(message="Fuel type not found.", status_code=404)
    if not transmission:
        return error_response(message="Transmission not found.", status_code=404)

    new_license_plate: str = normalize_license_plate(data["license_plate"])
    new_color: str = normalize_color(data["color"])
    new_model_name: str = data["model"].strip()

    existing_car: Car | None = get_car_by_license_plate(new_license_plate)
    if existing_car and existing_car.id != car.id:
        return error_response(message="Car with this license plate already exists.",status_code=409)

    old_values: dict[str, Any] = get_car_values(car.brand_id, car.category_id,car.fuel_type_id,
        car.transmission_id,car.model.name,car.license_plate,car.year,car.color,car.price_per_day,
        car.horse_power,car.seats,car.doors,car.description,car.status)

    car_changed: bool = False

    if car.brand_id != brand.id:
        car.brand_id = brand.id
        # Every car owns its own Model
        car.model.brand_id = brand.id
        car_changed = True

    if car.category_id != category.id:
        car.category_id = category.id
        car_changed = True

    if car.fuel_type_id != fuel_type.id:
        car.fuel_type_id = fuel_type.id
        car_changed = True

    if car.transmission_id != transmission.id:
        car.transmission_id = transmission.id
        car_changed = True

    if car.model.name != new_model_name:
        car.model.name = new_model_name
        car_changed = True

    if car.license_plate != new_license_plate:
        car.license_plate = new_license_plate
        car_changed = True

    if car.year != data["year"]:
        car.year = data["year"]
        car_changed = True

    if car.color != new_color:
        car.color = new_color
        car_changed = True

    if str(car.price_per_day) != str(data["price_per_day"]):
        car.price_per_day = data["price_per_day"]
        car_changed = True

    if car.horse_power != data["horse_power"]:
        car.horse_power = data["horse_power"]
        car_changed = True

    if car.seats != data["seats"]:
        car.seats = data["seats"]
        car_changed = True

    if car.doors != data["doors"]:
        car.doors = data["doors"]
        car_changed = True

    new_description: str | None = data.get("description")
    if car.description != new_description:
        car.description = new_description
        car_changed = True

    if "status" in data and car.status != data["status"]:
        car.status = data["status"]
        car_changed = True


    images_changed: bool = bool(images)

    if images_changed:
        image_errors: dict[str, str] = validate_car_image_updates(images)

        if image_errors:
            return error_response(message="Validation failed.",status_code=400,errors=image_errors)

        # every requested image already exists
        for image_number in images:
            car_image: CarImage | None = get_car_image_by_number(car_id=car.id,image_number=image_number)
            if not car_image:
                return error_response(message=f"Image {image_number} not found.",status_code=404)


    if not car_changed and not images_changed:
        return success_response(message="No changes detected.",data=serialize_car(car),status_code=200)


    if images_changed:
        old_images: list[dict[str, str]] = []

        try:
            #backup images from cloudinary
            for image_number in images:
                car_image: CarImage | None = get_car_image_by_number( car_id=car.id,image_number=image_number)
                if not car_image:
                    raise Exception(f"Image {image_number} not found.")

                cloudinary_image = get_cloudinary_car_image(car_image.public_id)
                if not cloudinary_image:
                    raise Exception(f"Cloudinary image not found: {car_image.public_id}")

                old_images.append({"public_id": cloudinary_image["public_id"],"secure_url": cloudinary_image["secure_url"]})

            #upload new images to cloudinary
            for image_number, image in images.items():
                upload_cloudinary_car_image(file=image,car_id=str(car.id),image_number=image_number, overwrite=True)

        except Exception:
            #Restore old images for failed
            for old_image in old_images:
                restore_cloudinary_car_image(public_id=old_image["public_id"],secure_url=old_image["secure_url"])

            raise

    db.session.commit()

    new_values: dict[str, Any] = get_car_values(car.brand_id,car.category_id,car.fuel_type_id,car.transmission_id,
        car.model.name,car.license_plate,car.year,car.color,car.price_per_day,car.horse_power,car.seats,car.doors,
        car.description,car.status)

    log_entity_action(
        action="UPDATE_CAR",
        user=user,
        entity_name="Car",
        entity_id=car.id,
        old_values=old_values,
        new_values=new_values
    )

    return success_response(
        message="Car updated successfully.",
        data=serialize_car(car),
        status_code=200
    )



def delete_car(car_id: str) -> tuple[Response, int]:

    if not is_valid_uuid(car_id):
        return error_response(message="Invalid car id.",status_code=400)

    car: Car | None = get_car_by_id(car_id)
    if not car:
        return error_response(message="Car not found.",status_code=404)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)
    print(user)
    if not user:
        return error_response(message="User not found.", status_code=404)

    if car.status != "Available":
        return error_response(message="Car cannot be deleted because it is not available.",status_code=409)

    old_values = {
        "brand": car.brand.name,
        "model": car.model.name,
        "license_plate": car.license_plate
    }

    try:
        public_ids: list[str] = [image.public_id for image in car.images]

        delete_cloudinary_car_images(public_ids)

        delete_car_from_db(car)
        db.session.delete(car.model)
    except Exception:
        db.session.rollback()
        raise

    db.session.commit()

    log_entity_action(action="DELETE_CAR", user=user, entity_name="Car", entity_id=car.id, old_values=old_values)
    return success_response( message="Car deleted successfully.", data=None, status_code=200)
