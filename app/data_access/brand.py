from app.extensions import db
from app.utils.database import commit
from app.models.brand import Brand
from app.utils.validators import is_valid_uuid


def get_brand_by_name(name: str) -> Brand | None:
    return Brand.query.filter_by(name=name).first()


def get_brand_by_id(brand_id: str) -> Brand | None:
    if not is_valid_uuid(brand_id):
        return None

    return db.session.get(Brand, brand_id)


def get_all() -> list[Brand]:
    return Brand.query.order_by(Brand.name.asc()).all()


def save_brand(brand: Brand) -> Brand:
    db.session.add(brand)
    commit()
    return brand