from typing import Any

from flask import Response
from flask_jwt_extended import get_jwt_identity

from app.models.brand import Brand
from app.models.user import User
from app.data_access.brand import get_brand_by_name, save_brand, get_all, get_brand_by_id
from app.utils.responses import error_response, success_response
from app.utils.validators import validate_create_brand, is_valid_uuid
from app.utils.normalize import normalize_brand_name
from app.schemas.brand_schema import serialize_brand, serialize_brands
from app.services.audit_log_service import log_entity_action
from app.services.user_service import get_user_by_id


def create_brand(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_create_brand(data)

    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    name: str = normalize_brand_name(data["name"])

    existing_brand: Brand | None = get_brand_by_name(name)

    if existing_brand:
        return error_response(message="Brand already exists.",status_code=409)

    brand: Brand = Brand(name=name)
    save_brand(brand)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)
    if not user:
        return error_response(message="User not found.",status_code=404)

    log_entity_action(action="CREATE_BRAND",user=user,new_values={"name": brand.name})

    return success_response(message="Brand created successfully.", data=serialize_brand(brand),status_code=201)


def get_all_brands() -> tuple[Response, int]:
    return success_response(data=serialize_brands(get_all()), status_code=200)


def get_brand(brand_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(brand_id):
        return error_response( message="Invalid brand id.", status_code=400
                               )
    brand: Brand | None = get_brand_by_id(brand_id)

    if not brand:
        return error_response(message="Brand not found.",status_code=404)

    return success_response(data=serialize_brand(brand))