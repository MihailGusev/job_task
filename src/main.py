from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session
from . import crud, models, schemas, security
from .database import engine, get_session, SessionLocal
import re

def setup():
    """There's no way of adding new users via API, so this function adds one"""
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    name = 'john'
    password = 'password'
    user = models.User(name=name, password=security.get_password_hash(password))
    db.add(user)
    db.commit()
    db.close()

setup()

get_history_pattern = re.compile('^history (?P<count>\d+)$')

app = FastAPI()


@app.post('/get-token')
def get_token(user: schemas.User, db: Session = Depends(get_session)):
    """Accepts name and password, returns JWT with name and expiration date"""
    db_user: models.User = crud.get_user_by_name(db, user.name)
    if db_user is None or not security.verify_password(user.password, db_user.password):
        raise_401('Incorrect name or password')
    token = security.create_access_token(user.name)
    return {'token': token}


@app.post('/send-message')
def send_message(message: schemas.Message, authorization: str = Header(), db: Session = Depends(get_session)):
    """
    Accepts message from the request body and token from authorization header
    The action depends on the message's format:
    1) 'history n' where n is an integer will return the last n messages
    2) any other message will be saved in the DB as a new message
    """
    prefix = 'Bearer_'
    if not authorization.startswith(prefix):
        raise_401(f'Authorization token must have {prefix} as a prefix')

    token = authorization[len(prefix):]

    name = security.get_user_name_from_token(token)
    if name is None:
        raise_401('Invalid token')
    if name != message.name:
        raise_401('Names in the token and in the body do not match')

    match = get_history_pattern.match(message.message)

    if match:
        count = match.group('count')
        return crud.get_last_messages(db, int(count))

    user: models.User = crud.get_user_by_name(db, name)
    if user is None:
        raise_401('User with this name does not exist')

    crud.create_message(db, message.message, user.id)
    return 'Message has been added'


def raise_401(detail: str):
    raise HTTPException(status_code=401, detail=detail)
