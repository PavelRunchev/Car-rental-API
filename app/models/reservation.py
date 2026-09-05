from app.extensions import db
from app.models.base import BaseModel


class Reservation(BaseModel):
    __tablename__ = "reservations"

    user_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("users.id"),nullable=False)

    car_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("cars.id"),nullable=False)

    start_date = db.Column(db.Date,nullable=False)

    end_date = db.Column(db.Date,nullable=False)

    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(db.Enum("Pending","Active","Confirmed","Completed","Cancelled",name="reservation_status"),nullable=False,default="Pending")

    user = db.relationship("User", back_populates="reservations")
    car = db.relationship("Car", back_populates="reservations")
    payment = db.relationship("Payment", back_populates="reservation",uselist=False)

    def __repr__(self):
        return f"<Reservation {self.id}>"