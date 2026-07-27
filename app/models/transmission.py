from app.extensions import db
from app.models.base import BaseModel


class Transmission(BaseModel):
    __tablename__ = "transmissions"

    name = db.Column(db.String(50),nullable=False,unique=True)

    def __repr__(self):
        return f"<Transmission {self.name}>"