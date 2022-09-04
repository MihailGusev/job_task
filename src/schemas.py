from pydantic import BaseModel


class Message(BaseModel):
    """This is the format of message we get when user wants to add a message or get message history"""
    name: str
    message: str


class User(BaseModel):
    """Used to create a new JWT token"""
    name: str
    password: str
