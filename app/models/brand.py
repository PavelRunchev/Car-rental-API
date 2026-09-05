from app.extensions import db
from app.models.base import BaseModel


class Brand(BaseModel):
    __tablename__ = "brands"

    name = db.Column( db.String(100), nullable=False, unique=True )

    cars = db.relationship("Car", back_populates="brand")
    models = db.relationship("Model", back_populates="brand")

    def __repr__(self):
        return f"<Brand {self.name}>"
