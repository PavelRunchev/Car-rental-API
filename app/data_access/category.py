from app.extensions import db
from app.utils.database import commit
from app.models.category import Category
from app.utils.validators import is_valid_uuid


def get_category_by_name(name: str) -> Category | None:
    return Category.query.filter_by(name=name).first()


def get_category_by_id(category_id: str) -> Category | None:
    if not is_valid_uuid(category_id):
        return None
    return db.session.get(Category, category_id)


def get_categories() -> list[Category]:
    return Category.query.order_by(Category.name.asc()).all()


def save_category(category: Category) -> Category:
    db.session.add(category)
    commit()
    return category

def delete_category_from_db(category: Category) -> None:
    db.session.delete(category)
    commit()

def update_category_in_db() -> None:
    commit()