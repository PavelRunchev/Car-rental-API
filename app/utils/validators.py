import re
from datetime import datetime
from re import Pattern
from typing import Any
from uuid import UUID
from decimal import Decimal
from werkzeug.datastructures import FileStorage

from app.utils.normalize import (
    normalize_phone,
    normalize_email,
    normalize_brand_name,
    normalize_model_name,
    normalize_category_name,
    normalize_license_plate,
    normalize_color
)

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 100
PASSWORD_MIN_LENGTH = 8

# ==========================
# AUTH
# ==========================
def is_valid_uuid(value: str) -> bool:
    try:
        UUID(str(value))
        return True
    except (ValueError, TypeError, AttributeError):
        return False

def is_valid_name(name: str) -> bool:
    name = name.strip()
    return NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.fullmatch(email))

def is_valid_password(password: str) -> bool:
    return (
        len(password) >= PASSWORD_MIN_LENGTH
        and any(c.isupper() for c in password)
        and any(c.islower() for c in password)
        and any(c.isdigit() for c in password)
    )

def is_valid_phone(phone: str | None) -> bool:
    if phone is None:
        return True

    return bool(PHONE_REGEX.fullmatch(phone))

def validate_register(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = validate_user_data(data)

    if not data.get("password"):
        errors["password"] = "Password is required."
    elif not is_valid_password(data["password"]):
        errors["password"] = (
            "Password must contain at least 8 characters, "
            "one uppercase letter, one lowercase letter and one digit."
        )

    return errors


def validate_user_data(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    required_fields = ["first_name","last_name","email","phone"]
    for field in required_fields:
        if not data.get(field):
            errors[field] = "This field is required."

    if errors:
        return errors

    if not is_valid_name(data["first_name"]):
        errors["first_name"] = f"First name must be between {NAME_MIN_LENGTH} and {NAME_MAX_LENGTH} characters."

    if not is_valid_name(data["last_name"]):
        errors["last_name"] = f"Last name must be between {NAME_MIN_LENGTH} and {NAME_MAX_LENGTH} characters."

    if not is_valid_email(data["email"]):
        errors["email"] = "Invalid email address."

    phone = normalize_phone(data["phone"])
    if not is_valid_phone(phone):
        errors["phone"] = "Invalid phone number."

    return errors


def validate_operator_user(data: dict[str, Any]) -> dict[str, str]:
    return validate_user_data(data)


def validate_login(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    required_fields = ["email","password"]
    for field in required_fields:
        if not data.get(field):
            errors[field] = "This field is required."
    if errors:
        return errors

    if not is_valid_email(data["email"]):
        errors["email"] = "Invalid email or password"

    return errors

def validate_refresh_token(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("refresh_token"):
        errors["refresh_token"] = "This field is required."

    return errors

# ==========================
# PROFILE
# ==========================

def validate_profile_update(data: dict) -> dict[str, str]:
    errors: dict[str, str] = {}

    required_fields = ["first_name","last_name","phone",]

    for field in required_fields:
        if not data.get(field):
            errors[field] = "This field is required."

    if errors:
        return errors

    if not is_valid_name(data["first_name"]):
        errors["first_name"] = (
            f"First name must be between "
            f"{NAME_MIN_LENGTH} and {NAME_MAX_LENGTH} characters."
        )

    if not is_valid_name(data["last_name"]):
        errors["last_name"] = (
            f"Last name must be between "
            f"{NAME_MIN_LENGTH} and {NAME_MAX_LENGTH} characters."
        )

    if not is_valid_phone(data["phone"]):
        errors["phone"] = "Invalid phone number."

    return errors

def validate_email_update(data: dict) -> dict[str, str]:
    errors: dict[str, str] = {}
    email: str = data.get("email")

    if not email:
        errors["email"] = "This field is required."
        return errors

    email = normalize_email(email)

    if not is_valid_email(email):
        errors["email"] = "Invalid email address."

    return errors

def validate_password_update(data: dict) -> dict[str, str]:
    errors: dict[str, str] = {}

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password:
        errors["current_password"] = "This field is required."

    if not new_password:
        errors["new_password"] = "This field is required."

    if not confirm_password:
        errors["confirm_password"] = "This field is required."

    if errors:
        return errors

    if not is_valid_password(new_password):
        errors["new_password"] = (
            "Password must be at least 8 characters long and contain "
            "at least one uppercase letter, one lowercase letter, "
            "one digit and one special character."
        )

    return errors

# ==========================
# BRAND
# ==========================
BRAND_NAME_REGEX = re.compile(r"^[A-Za-z0-9À-ÿА-Яа-я .&'()-]+$")
BRAND_NAME_MIN_LENGTH = 2
BRAND_NAME_MAX_LENGTH = 100

def validate_brand(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not data.get("name"):
        errors["name"] = "Brand name is required."
        return errors

    name: str = normalize_brand_name(data["name"])

    if len(name) < BRAND_NAME_MIN_LENGTH:
        errors["name"] = f"Brand name must be at least {BRAND_NAME_MIN_LENGTH} characters long."

    elif len(name) > BRAND_NAME_MAX_LENGTH:
        errors["name"] = f"Brand name must be at most {BRAND_NAME_MAX_LENGTH} characters long."

    elif not BRAND_NAME_REGEX.fullmatch(name):
        errors["name"] = "Brand name contains invalid characters."

    return errors


def validate_create_brand(data: dict[str, Any]) -> dict[str, str]:
    return validate_brand(data)


def validate_update_brand(data: dict[str, Any]) -> dict[str, str]:
    return validate_brand(data)


# ==========================
# MODEL
# ==========================
MODEL_NAME_MIN_LENGTH: int = 2
MODEL_NAME_MAX_LENGTH: int = 100
MODEL_NAME_REGEX: Pattern[str] = re.compile(r"^[A-Za-z0-9\s\-]+$")

def validate_model_name(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not data.get("name"):
        errors["name"] = "Model name is required."
        return errors

    name: str = normalize_model_name(data["name"])

    if len(name) < MODEL_NAME_MIN_LENGTH:
        errors["name"] = f"Model name must be at least {MODEL_NAME_MIN_LENGTH} characters long."
    elif len(name) > MODEL_NAME_MAX_LENGTH:
        errors["name"] = f"Model name must be at most {MODEL_NAME_MAX_LENGTH} characters long."
    elif not MODEL_NAME_REGEX.fullmatch(name):
        errors["name"] = "Model name contains invalid characters."

    return errors

def validate_create_model(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not data.get("brand_id"):
        errors["brand_id"] = "Brand is required."

    errors.update(validate_model_name(data))
    return errors

def validate_update_model(data: dict[str, Any]) -> dict[str, str]:
    return validate_model_name(data)

# ==========================
# CATEGORY
# ==========================
CATEGORY_NAME_MIN_LENGTH: int = 2
CATEGORY_NAME_MAX_LENGTH: int = 50
CATEGORY_NAME_REGEX: Pattern[str] = re.compile(r"^[A-Za-z0-9\s\-]+$")


def validate_category_name(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("name"):
        errors["name"] = "Category name is required."
        return errors

    name: str = normalize_category_name(data["name"])
    if len(name) < CATEGORY_NAME_MIN_LENGTH:
        errors["name"] = f"Category name must be at least {CATEGORY_NAME_MIN_LENGTH} characters long."
    elif len(name) > CATEGORY_NAME_MAX_LENGTH:
        errors["name"] = f"Category name must be at most {CATEGORY_NAME_MAX_LENGTH} characters long."
    elif not CATEGORY_NAME_REGEX.fullmatch(name):
        errors["name"] = "Category name contains invalid characters."

    return errors


def validate_create_category(data: dict[str, Any]) -> dict[str, str]:
    return validate_category_name(data)


def validate_update_category(data: dict[str, Any]) -> dict[str, str]:
    return validate_category_name(data)

# ==========================
# CAR
# ==========================
CAR_YEAR_MIN: int = 1900
CAR_PRICE_PER_DAY_MIN: Decimal = Decimal("0.01")
CAR_HORSE_POWER_MIN: int = 1
CAR_SEATS_MIN: int = 1
CAR_SEATS_MAX: int = 9
CAR_DOORS_MIN: int = 2
CAR_DOORS_MAX: int = 5

CAR_LICENSE_PLATE_MIN_LENGTH: int = 3
CAR_LICENSE_PLATE_MAX_LENGTH: int = 15
CAR_LICENSE_PLATE_REGEX: Pattern[str] = re.compile(r"^[A-Z0-9\s\-]+$")

CAR_COLOR_MIN_LENGTH: int = 2
CAR_COLOR_MAX_LENGTH: int = 50
CAR_COLOR_REGEX: Pattern[str] = re.compile(r"^[A-Za-z\s\-]+$")
IMAGE_EXTENSION_PATTERN = re.compile(r"^.+\.(jpg|jpeg|png|webp)$",re.IGNORECASE)

CAR_DESCRIPTION_MAX_LENGTH: int = 1000
CAR_STATUSES: set[str] = {"Available","Reserved","Maintenance"}


def validate_model(value: Any) -> str | None:
    if not value:
        return "Model is required."

    if not isinstance(value, str):
        return "Model must be a string."

    model: str = value.strip()
    if not model:
        return "Model is required."

    if len(model) > 100:
        return "Model must be at most 100 characters long."

    return None


def validate_license_plate(value: Any) -> str | None:
    if not value:
        return "License plate is required."

    plate: str = normalize_license_plate(value)
    if len(plate) < CAR_LICENSE_PLATE_MIN_LENGTH:
        return f"License plate must be at least {CAR_LICENSE_PLATE_MIN_LENGTH} characters long."

    if len(plate) > CAR_LICENSE_PLATE_MAX_LENGTH:
        return f"License plate must be at most {CAR_LICENSE_PLATE_MAX_LENGTH} characters long."

    if not CAR_LICENSE_PLATE_REGEX.fullmatch(plate):
        return "License plate contains invalid characters."

    return None


def validate_car_year(value: Any) -> str | None:
    if value is None:
        return "Year is required."

    if not isinstance(value, int):
        return "Year must be a number."

    if value < CAR_YEAR_MIN:
        return f"Year must be at least {CAR_YEAR_MIN}."

    return None


def validate_car_color(value: Any) -> str | None:
    if not value:
        return "Color is required."

    color: str = normalize_color(value)
    if len(color) < CAR_COLOR_MIN_LENGTH:
        return f"Color must be at least {CAR_COLOR_MIN_LENGTH} characters long."

    if len(color) > CAR_COLOR_MAX_LENGTH:
        return f"Color must be at most {CAR_COLOR_MAX_LENGTH} characters long."

    if not CAR_COLOR_REGEX.fullmatch(color):
        return "Color contains invalid characters."

    return None


def validate_price_per_day(value: Any) -> str | None:
    if value is None:
        return "Price per day is required."

    try:
        price: Decimal = Decimal(str(value))
    except (ValueError, TypeError):
        return "Price per day must be a valid number."

    if price < CAR_PRICE_PER_DAY_MIN:
        return f"Price per day must be at least {CAR_PRICE_PER_DAY_MIN}."

    return None


def validate_horse_power(value: Any) -> str | None:
    if value is None:
        return "Horse power is required."

    if not isinstance(value, int):
        return "Horse power must be a number."

    if value < CAR_HORSE_POWER_MIN:
        return f"Horse power must be at least {CAR_HORSE_POWER_MIN}."

    return None


def validate_seats(value: Any) -> str | None:
    if value is None:
        return "Seats are required."

    if not isinstance(value, int):
        return "Seats must be a number."

    if not CAR_SEATS_MIN <= value <= CAR_SEATS_MAX:
        return f"Seats must be between {CAR_SEATS_MIN} and {CAR_SEATS_MAX}."

    return None


def validate_doors(value: Any) -> str | None:
    if value is None:
        return "Doors are required."

    if not isinstance(value, int):
        return "Doors must be a number."

    if not CAR_DOORS_MIN <= value <= CAR_DOORS_MAX:
        return f"Doors must be between {CAR_DOORS_MIN} and {CAR_DOORS_MAX}."

    return None


def validate_description(value: Any) -> str | None:
    if value is None or value == "":
        return None

    if not isinstance(value, str):
        return "Description must be a string."

    if len(value) > CAR_DESCRIPTION_MAX_LENGTH:
        return f"Description must be at most {CAR_DESCRIPTION_MAX_LENGTH} characters long."

    return None


def validate_car_status(value: Any) -> str | None:
    if value is None:
        return None

    if value not in CAR_STATUSES:
        return "Invalid car status."

    return None


def validate_image_extension(filename: Any) -> str | None:
    if not filename:
        return "Image filename is required."

    if not isinstance(filename, str):
        return "Image filename must be a string."

    if not IMAGE_EXTENSION_PATTERN.fullmatch(filename.strip()):
        return "Unsupported image format. Allowed formats: JPG, JPEG, PNG and WEBP."

    return None


def validate_image_file(file: FileStorage | None) -> str | None:
    if file is None:
        return "Image file is required."

    filename: str = file.filename or ""
    if not filename:
        return "Image filename is required."

    if not IMAGE_EXTENSION_PATTERN.fullmatch(filename):
        return "Unsupported image format. Allowed formats: JPG, JPEG, PNG and WEBP."

    return None

MAX_IMAGE_SIZE = 10 * 1024 * 1024
def validate_image_size(file: FileStorage | None) -> str | None:
    if file is None:
        return "Image file is required."

    file.stream.seek(0, 2)
    file_size: int = file.stream.tell()
    file.stream.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return "Image size must not exceed 10 MB."

    return None


def validate_image(file: FileStorage | None) -> str | None:
    if file is None:
        return "Image file is required."

    filename: str = file.filename or ""
    error = validate_image_extension(filename)
    if error:
        return error

    error = validate_image_file(file)
    if error:
        return error

    error = validate_image_size(file)
    if error:
        return error

    return None


MAX_CAR_IMAGES = 5
def validate_car_images(images: list[FileStorage]) -> str | None:
    if len(images) > MAX_CAR_IMAGES:
        return "A car can have a maximum of 5 images."

    for image in images:
        error = validate_image(image)

        if error:
            return error

    return None


def validate_car(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    validators = {
        "model": validate_model,
        "license_plate": validate_license_plate,
        "year": validate_car_year,
        "color": validate_car_color,
        "price_per_day": validate_price_per_day,
        "horse_power": validate_horse_power,
        "seats": validate_seats,
        "doors": validate_doors,
        "description": validate_description,
        "status": validate_car_status,
    }

    for key, validator in validators.items():
        error: str | None = validator(data.get(key))

        if error:
            errors[key] = error

    return errors


def validate_car_image_updates(images: dict[int, FileStorage]) -> dict[str, str]:
    errors: dict[str, str] = {}

    for image_number, image in images.items():
        if image_number < 1 or image_number > 5:
            errors[f"image_{image_number}"] = ("Image number must be between 1 and 5.")
            continue

        error: str | None = validate_image(image)

        if error:
            errors[f"image_{image_number}"] = error

    return errors



# ==========================
# RESERVATION
# ==========================
def validate_reservation(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not data.get("car_id"):
        errors["car_id"] = "Car id is required."
    elif not is_valid_uuid(data["car_id"]):
        errors["car_id"] = "Invalid car id."

    if not data.get("start_date"):
        errors["start_date"] = "Start date is required."

    if not data.get("end_date"):
        errors["end_date"] = "End date is required."

    if data.get("start_date") and data.get("end_date"):
        try:
            start_date = datetime.strptime(data["start_date"],"%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"],"%Y-%m-%d").date()

            if start_date >= end_date:
                errors["end_date"] = "End date must be after start date."

        except ValueError:
            errors["start_date"] = "Invalid start date format."
            errors["end_date"] = "Invalid end date format."

    if data.get("status") and data["status"] not in {"Active","Completed","Cancelled"}:
        errors["status"] = "Invalid reservation status."


    return errors


