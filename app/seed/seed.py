from app.extensions import db

from app.models.brand import Brand
from app.models.category import Category
from app.models.fuel_type import FuelType
from app.models.transmission import Transmission

from app.seed.brands import BRANDS
from app.seed.categories import CATEGORIES
from app.seed.fuel_types import FUEL_TYPES
from app.seed.transmissions import TRANSMISSIONS

def seed_brands():
    # Brands
    for name in BRANDS:
        if not Brand.query.filter_by(name=name).first():
            db.session.add(Brand(name=name))

def seed_categories():
    # Categories
    for name in CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

def seed_fuel_types():
    # Fuel Types
    for name in FUEL_TYPES:
        if not FuelType.query.filter_by(name=name).first():
            db.session.add(FuelType(name=name))

def seed_transmissions():
    # Transmissions
    for name in TRANSMISSIONS:
        if not Transmission.query.filter_by(name=name).first():
            db.session.add(Transmission(name=name))

def seed_database():
    seed_brands()
    seed_categories()
    seed_fuel_types()
    seed_transmissions()
    db.session.commit()
    print("✅ Database seeded successfully!")