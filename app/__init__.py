from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate
import app.models

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    return app