from app.extensions import db
from app.models.base import BaseModel


class Model(BaseModel):
    __tablename__ = "models"

    name = db.Column( db.String(100), nullable=False )

    brand_id = db.Column( db.UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=False )

    brand = db.relationship( "Brand", back_populates="models" )

    cars = db.relationship("Car",back_populates="model")


