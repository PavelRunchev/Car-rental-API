from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.seed.seed import seed_database
from app.controllers.auth_routes import auth_bp
from app.controllers.profile_routes import profile_bp
from app.handlers.error_handler import register_error_handlers
import app.models
from app.controllers.brand_routes import brand_bp
from app.controllers.model_routes import model_bp
from app.controllers.category_routes import category_bp
from app.controllers.transmission_routes import transmission_bp
from app.controllers.fuel_type_routes import fuel_type_bp
from app.controllers.car_routes import car_bp
from app.controllers.cloudinary_routes import cloudinary_bp
from app.controllers.reservation_routes import reservation_bp
from app.controllers.activate_account import activate_account_bp
from app.controllers.payment_routes import payment_bp
import cloudinary
import stripe

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    stripe.api_key = app.config["STRIPE_SECRET_KEY"]

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    register_error_handlers(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(transmission_bp)
    app.register_blueprint(fuel_type_bp)
    app.register_blueprint(car_bp)
    app.register_blueprint(cloudinary_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(activate_account_bp)
    app.register_blueprint(payment_bp)

    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    @app.cli.command("seed")
    def seed():
        seed_database()


    @app.route("/")
    def home():
        return {"success": True,"message": "Car Rental API is running."}, 200


    return app

