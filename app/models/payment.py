from app.extensions import db
from app.models.base import BaseModel

class Payment(BaseModel):
    __tablename__ = "payments"

    reservation_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("reservations.id"),nullable=False,unique=True)

    user_id = db.Column(db.UUID(as_uuid=True),db.ForeignKey("users.id"),nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    currency = db.Column(db.String(3), nullable=False, default="EUR")

    status = db.Column(db.Enum("Pending","Paid","Failed","Cancelled","Refunded", name="payment_status"),
        nullable=False, default="Pending"
    )

    payment_method = db.Column( db.Enum("Online","Terminal", name="payment_method"), nullable=False )

    provider = db.Column(db.String(50),nullable=False, default="Stripe")

    provider_payment_id = db.Column(db.String(255),nullable=True,unique=True)

    reservation = db.relationship("Reservation", back_populates="payment")
    user = db.relationship("User")

