from typing import Any
from flask import Response
from flask_jwt_extended import get_jwt_identity

from app.models.category import Category
from app.models.user import User

from app.utils.responses import error_response, success_response
from app.utils.validators import validate_create_category, is_valid_uuid, validate_update_category
from app.utils.normalize import normalize_category_name
from app.data_access.category import (
    get_category_by_name,
    save_category,
    get_categories,
    get_category_by_id,
    update_category_in_db,
    delete_category_from_db
)
from app.services.user_service import get_user_by_id
from app.services.audit_log_service import log_entity_action
from app.schemas.category_schema import serialize_category, serialize_categories


def create_category(data: dict[str, Any]) -> tuple[Response, int]:
    errors: dict[str, str] = validate_create_category(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    name: str = normalize_category_name(data["name"])

    existing_category: Category | None = get_category_by_name(name)
    if existing_category:
        return error_response(message="Category already exists.",status_code=409)

    category: Category = Category(name=name)
    save_category(category)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)
    if not user:
        return error_response(message="User not found.",status_code=404)

    log_entity_action(action="CREATE_CATEGORY", user=user, new_values={"name": category.name} )

    return success_response( message="Category created successfully.", data=serialize_category(category), status_code=201 )


def get_all_categories() -> tuple[Response, int]:
    return success_response(data=serialize_categories(get_categories()), status_code=200)


def get_category(category_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(category_id):
        return error_response( message="Invalid category id.", status_code=400
                               )
    category: Category | None = get_category_by_id(category_id)

    if not category:
        return error_response(message="Category not found.",status_code=404)

    return success_response(data=serialize_category(category))


def update_category(category_id: str, data: dict[str, Any]) -> tuple[Response, int]:
    if not is_valid_uuid(category_id):
        return error_response(message="Invalid category id.",status_code=400)

    category: Category | None = get_category_by_id(category_id)
    if not category:
        return error_response(message="Category not found.",status_code=404)

    errors: dict[str, str] = validate_update_category(data)
    if errors:
        return error_response(message="Validation failed.",status_code=400,errors=errors)

    name: str = normalize_category_name(data["name"])
    existing_category: Category | None = get_category_by_name(name)
    if existing_category and existing_category.id != category.id:
        return error_response(message="Category already exists.",status_code=409)

    if category.name == name:
        return success_response(message="No changes detected.",data=serialize_category(category), status_code=200)

    old_values = {"name": category.name}
    category.name = name
    update_category_in_db()

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if user:
        log_entity_action(action="UPDATE_CATEGORY",user=user,old_values=old_values,new_values={"name": category.name})

    return success_response(message="Category updated successfully.",data=serialize_category(category), status_code=200)


def delete_category(category_id: str) -> tuple[Response, int]:
    if not is_valid_uuid(category_id):
        return error_response(message="Invalid category id.", status_code=400)

    category: Category | None = get_category_by_id(category_id)
    if not category:
        return error_response(message="Category not found.",status_code=404)

    user_id: str = get_jwt_identity()
    user: User | None = get_user_by_id(user_id)

    if user:
        log_entity_action(action="DELETE_CATEGORY",user=user,old_values={"name": category.name})

    delete_category_from_db(category)

    return success_response(message="Category deleted successfully.",status_code=200)