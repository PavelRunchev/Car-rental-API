from app.extensions import db
from app.models.base import BaseModel


class Brand(BaseModel):
    __tablename__ = "brands"

    name = db.Column( db.String(100), nullable=False, unique=True )

    logo_public_id = db.Column( db.String(255), nullable=True )

    def __repr__(self):
        return f"<Brand {self.name}>"