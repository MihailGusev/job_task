from sqlalchemy.orm import Session
from .models import Message, User


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def get_last_messages(db: Session, count: int = 10):
    """Get last messages (message itself and name of the user who posted it)"""
    return db.query(Message).join(User).order_by(
        Message.id.desc()).limit(count).values(Message.message, User.name)


def create_message(db: Session, message: str, user_id: int):
    message = Message(message=message, sender_id=user_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
