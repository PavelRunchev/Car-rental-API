from app.extensions import db
from app.models.support_topic import SupportTopic
from app.utils.database import commit
from app.utils.validators import is_valid_uuid


def get_support_topic_by_id(topic_id: str) -> SupportTopic | None:
    if not is_valid_uuid(topic_id):
        return None

    return db.session.get(SupportTopic, topic_id)


def get_support_topics() -> list[SupportTopic]:
    return SupportTopic.query.order_by(SupportTopic.updated_at.desc()).all()


def save_support_topic(topic: SupportTopic) -> SupportTopic:
    db.session.add(topic)
    commit()
    return topic


def delete_support_topic(topic: SupportTopic) -> None:
    db.session.delete(topic)
    commit()


def update_support_topic(topic: SupportTopic) -> SupportTopic:
    commit()
    return topic

