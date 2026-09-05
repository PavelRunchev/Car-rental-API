from flask import Blueprint, Response, request
from app.decorators.roles_required import roles_required
from app.services.cloudinary_service import (
    upload_cloudinary_car_image,
    get_all_cloudinary_car_images,
    get_cloudinary_car_image,
    delete_cloudinary_car_image,
)

from app.utils.responses import error_response, success_response

cloudinary_bp = Blueprint("cloudinary",__name__,url_prefix="/api/cloudinary")

@roles_required("Admin", "Operator")
@cloudinary_bp.route("", methods=["POST"])
def upload_image() -> tuple[Response, int]:
    image = request.files.get("image")

    if image is None:
        return Response("Image file is required.",status=400), 400

    public_id: str = upload_cloudinary_car_image(file=image,car_id="test-car",image_number=1)
    return Response(public_id,status=201), 201

@roles_required("Admin", "Operator", "User")
@cloudinary_bp.route("/images", methods=["GET"])
def get_images_controller() -> tuple[Response, int]:
    images: list[dict] = get_all_cloudinary_car_images()
    return success_response(data=images,status_code=200)

@roles_required("Admin", "Operator", "User")
@cloudinary_bp.route("/image", methods=["GET"])
def get_image_controller() -> tuple[Response, int]:

    public_id: str | None = request.args.get("public_id")
    if not public_id:
        return error_response(message="Public ID is required.",status_code=400)

    image: dict | None = get_cloudinary_car_image(public_id)
    if not image:
        return error_response(message="Image not found.",status_code=404)

    return success_response(data=image,status_code=200)

@roles_required("Admin", "Operator")
@cloudinary_bp.route("/image", methods=["DELETE"])
def delete_image_controller() -> tuple[Response, int]:

    public_id: str | None = request.args.get("public_id")
    if not public_id:
        return error_response(message="Public ID is required.",status_code=400)

    image: dict | None = get_cloudinary_car_image(public_id)
    if not image:
        return error_response(message="Image not found.",status_code=404)

    delete_cloudinary_car_image(public_id)
    return success_response(message="Image deleted successfully.",status_code=200)