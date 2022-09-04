from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)

    messages = relationship("Message", back_populates="sender")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)

    sender_id = Column(Integer, ForeignKey("users.id"))

    sender = relationship("User", back_populates="messages")
