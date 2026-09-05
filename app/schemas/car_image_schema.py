from app.models.car_image import CarImage


def serialize_car_image(image: CarImage) -> dict:
    return {
        "id": str(image.id),
        "car_id": str(image.car_id),
        "public_id": image.public_id,
        "is_primary": image.is_primary,
        "created_at": image.created_at.isoformat(),
        "updated_at": image.updated_at.isoformat(),
    }


def serialize_car_images(images: list[CarImage]) -> list[dict]:
    return [serialize_car_image(image) for image in images]