from app.extensions import db
from app.models.base import BaseModel


class FuelType(BaseModel):
    __tablename__ = "fuel_types"

    name = db.Column(db.String(50),nullable=False,unique=True)

    def __repr__(self):
        return f"<FuelType {self.name}>"