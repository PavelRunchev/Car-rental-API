from typing import Any
from flask import Response

from app.models.model import Model
from app.models.brand import Brand
from app.models.user import User

from app.data_access.model import get_model_by_name, get_model_by_id, get_all, save_model, delete_model_from_db, commit_changes
from app.data_access.brand import get_brand_by_id
from app.utils.responses import error_response,success_response
from app.utils.validators import validate_create_model, is_valid_uuid, validate_update_model
from app.utils.normalize import normalize_model_name
from app.schemas.model_schema import serialize_model,serialize_models

from app.services.audit_log_service import log_entity_action
from flask_jwt_extended import get_jwt_identity
from app.services.user_service import get_user_by_id


def create_model(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_create_model(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    name: str = normalize_model_name(data["name"])
    brand_id: str = data["brand_id"]

    brand: Brand | None = get_brand_by_id(brand_id)
    if not brand:
        return error_response(message="Brand not found.",status_code=404)

    existing_model: Model | None = get_model_by_name(name,brand_id)

    if existing_model:
        return error_response(message="Model already exists for this brand.",status_code=409)

    model: Model = Model(name=name,brand_id=brand.id)
    save_model(model)

    user_id: str = get_jwt_identity()
    user = get_user_by_id(user_id)

    if user:
        log_entity_action( action="CREATE_MODEL", user=user, new_values={"name": model.name,"brand": brand.name} )

    return success_response( message="Model created successfully.", data=serialize_model(model), status_code=201 )


def get_all_models() -> tuple[Response, int]:
    return success_response(data=serialize_models(get_all()),status_code=200)


def get_model(model_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(model_id):
        return error_response( message="Invalid model id.", status_code=400
                               )
    model: Model | None = get_model_by_id(model_id)

    if not model:
        return error_response(message="Model not found.",status_code=404)

    return success_response(data=serialize_model(model), status_code=200)


def delete_model(model_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(model_id):
        return error_response(message="Invalid model id.",status_code=400)

    model: Model | None = get_model_by_id(model_id)
    if not model:
        return error_response(message="Model not found.",status_code=404)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)
    if not user:
        return error_response(message="User not found.",status_code=404)

    log_entity_action(action="DELETE_MODEL",user=user,old_values={"name": model.name,"brand": model.brand.name})
    delete_model_from_db(model)

    return success_response(message="Model deleted successfully.",status_code=200)


def update_model(model_id: str, data: dict[str, Any]) -> tuple[Response, int]:
    if not is_valid_uuid(model_id):
        return error_response(message="Invalid model id.",status_code=400)

    model: Model | None = get_model_by_id(model_id)
    if not model:
        return error_response(message="Model not found.",status_code=404)

    errors: dict[str, str] = validate_update_model(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    name: str = normalize_model_name(data["name"])
    brand_id: str = data["brand_id"]

    brand: Brand | None = get_brand_by_id(brand_id)

    if not brand:
        return error_response(message="Brand not found.",status_code=404)

    existing_model: Model | None = get_model_by_name(name,brand_id)

    if existing_model and existing_model.id != model.id:
        return error_response(message="Model already exists for this brand.",status_code=409)

    old_values = { "name": model.name, "brand": model.brand.name }

    if model.name == name and model.brand_id == brand.id:
        return success_response(message="No changes detected.", data=serialize_model(model), status_code=200)

    model.name = name
    model.brand_id = brand.id
    commit_changes()

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if user:
        log_entity_action(action="UPDATE_MODEL",user=user, old_values=old_values, new_values={"name": model.name,"brand": brand.name})

    return success_response(message="Model updated successfully.",data=serialize_model(model),status_code=200)