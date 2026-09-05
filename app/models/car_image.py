from app.extensions import db
from app.models.base import BaseModel


class CarImage(BaseModel):
    __tablename__ = "car_images"

    car_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("cars.id"),nullable=False)

    public_id = db.Column(db.String(255),nullable=False)

    is_primary = db.Column(db.Boolean,nullable=False,default=False)

    def __repr__(self):
        return f"<CarImage {self.public_id}>"

