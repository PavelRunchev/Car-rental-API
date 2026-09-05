from app.extensions import db
from app.models.base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel):
    __tablename__ = "users"

    first_name = db.Column(db.String(100),nullable=False)

    last_name = db.Column(db.String(100),nullable=False)

    email = db.Column(db.String(255),nullable=False,unique=True)

    password_hash = db.Column(db.String(255),nullable=True)

    must_set_password = db.Column(db.Boolean,nullable=False,default=True)

    phone = db.Column(db.String(30),nullable=False)

    role = db.Column(db.Enum("Admin", "Operator","User",name="user_role"),nullable=False,default="User")

    is_active = db.Column(db.Boolean,nullable=False,default=True)

    reservations = db.relationship("Reservation",back_populates="user")

    activation_tokens = db.relationship("ActivationToken",back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


