import cloudinary
import cloudinary.api
import cloudinary.uploader
from werkzeug.datastructures import FileStorage
from typing import Any

def upload_cloudinary_car_image(file: FileStorage,car_id: str,image_number: int,overwrite: bool = False) -> str:
    public_id = f"cars/{car_id}/image_{image_number}"

    result: dict[str, Any] = cloudinary.uploader.upload(
        file,
        public_id=public_id,
        overwrite=overwrite,
        invalidate=overwrite,
        resource_type="image"
    )

    return result["public_id"]


def get_all_cloudinary_car_images() -> list[dict[str, Any]]:
    result = cloudinary.api.resources(resource_type="image",type="upload",prefix="cars/")
    return result.get("resources", [])


def get_cloudinary_car_image(public_id: str) -> dict[str, Any] | None:
    try:
        result = cloudinary.api.resource( public_id,resource_type="image",type="upload")
        return result
    except cloudinary.exceptions.NotFound:
        return None


def delete_cloudinary_car_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id,resource_type="image", type="upload", invalidate=True)


def delete_cloudinary_car_images(public_ids: list[str]) -> None:
    for public_id in public_ids:
        delete_cloudinary_car_image(public_id)


def restore_cloudinary_car_image(public_id: str,secure_url: str) -> None:
    cloudinary.uploader.upload(secure_url,public_id=public_id,overwrite=True,invalidate=True,resource_type="image")
