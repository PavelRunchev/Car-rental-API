from app.extensions import db
from app.utils.database import commit
from app.models.model import Model
from uuid import UUID, uuid4

def get_model_by_name(name: str, brand_id: str) -> Model | None:
    return Model.query.filter_by(name=name, brand_id=brand_id).first()


def get_model_by_id(model_id: str) -> Model | None:
    return db.session.get(Model, model_id)


def get_all() -> list[Model]:
    return Model.query.order_by(Model.name.asc()).all()


def save_model(model: Model) -> Model:
    db.session.add(model)
    commit()
    return model

def delete_model_from_db(model: Model) -> None:
    db.session.delete(model)
    commit()

def commit_changes() -> None:
    commit()


# def get_model_by_name_and_brand(name: str,brand_id: UUID) -> Model | None:
#     return db.session.execute(db.select(Model).where(Model.name == name,Model.brand_id == brand_id)).scalar_one_or_none()


def create_model(name: str, brand_id: UUID) -> Model:
    model = Model( id=uuid4(), name=name, brand_id=brand_id )
    db.session.add(model)
    return model

