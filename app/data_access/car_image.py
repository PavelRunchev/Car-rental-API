from app.extensions import db
from uuid import UUID
from app.models.car_image import CarImage


def get_car_image_by_number(car_id: UUID, image_number: int) -> CarImage | None:
    return db.session.execute(
        db.select(CarImage).where(
            CarImage.car_id == car_id,
            CarImage.public_id == f"cars/{car_id}/image_{image_number}"
        )
    ).scalar_one_or_none()

