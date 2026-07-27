from app.extensions import db
from app.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(50),nullable=False,unique=True)

    def __repr__(self):
        return f"<Category {self.name}>"