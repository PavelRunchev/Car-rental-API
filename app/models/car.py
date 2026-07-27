from app.extensions import db
from app.models.base import BaseModel


class Car(BaseModel):
    __tablename__ = "cars"

    brand_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("brands.id"),nullable=False)

    category_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("categories.id"),nullable=False)

    fuel_type_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("fuel_types.id"),nullable=False)

    transmission_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("transmissions.id"),nullable=False)

    model = db.Column(db.String(100),nullable=False)

    year = db.Column(db.Integer,nullable=False)

    color = db.Column(db.String(50),nullable=False)

    price_per_day = db.Column(db.Numeric(10, 2),nullable=False)

    horse_power = db.Column(db.Integer,nullable=False)

    seats = db.Column(db.Integer,nullable=False)

    doors = db.Column(db.Integer,nullable=False)

    description = db.Column(db.Text,nullable=True)

    status = db.Column(db.Enum("Available","Reserved","Maintenance",name="car_status"),nullable=False,default="Available")

    def __repr__(self):
        return f"<Car {self.model}>"