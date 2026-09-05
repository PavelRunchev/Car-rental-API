from app.extensions import db

def commit() -> None:
    db.session.commit()