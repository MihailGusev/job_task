from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

from .database import Base, get_session, get_engine
from .main import app
from .models import User, Message
from .security import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_messages.db"

engine = get_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

name = 'john'
password = 'password'
messages = [{'message': '1', 'name': name}]
known_user = {'name': name, 'password': password}
valid_token = create_access_token(name)


def override_get_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def setup():
    app.dependency_overrides[get_session] = override_get_session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSessionLocal()
    user = User(name=name, password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    message = Message(message='1', sender_id=user.id)
    db.add(message)
    db.commit()
    db.close()


setup()


def get_message(valid_user=True, history_format=True, count=10, message='1'):
    """Helper function to create new messages for /send-message path"""
    if not valid_user:
        return {'name': 'unknown', 'message': 'message'}
    if history_format:
        return {'name': name, 'message': f'history {count}'}
    return {'name': name, 'message': message}


def test_get_token_unknown_name():
    """/get-valid_token user is not in the db"""
    response = client.post(
        "/get-token",
        json={'name': 'unknown', 'password': password},
    )
    assert response.status_code == 401


def test_get_token_unknown_password():
    """/get-valid_token user is in the db, but passwords do not match"""
    response = client.post(
        "/get-token",
        json={'name': name, 'password': 'unknown'},
    )
    assert response.status_code == 401


def test_get_token_known_user():
    """/get-valid_token user is in the db and passwords match"""
    response = client.post(
        "/get-token",
        json=known_user,
    )
    assert response.status_code == 200


def test_send_no_message():
    """/send-message there's no message in the body"""
    response = client.post("/send-message")
    assert response.status_code == 422


def test_send_no_token():
    """/send-message there's no valid_token in the header"""
    response = client.post("/send-message", json=get_message())
    assert response.status_code == 422


def test_send_incorrect_token_format():
    """/send-message the token does not start with _Bearer"""
    response = client.post("/send-message",
                           json=get_message(),
                           headers={'authorization': f'Bearer {valid_token}'})
    assert response.status_code == 401


def test_send_incorrect_token():
    """/send-message the token contains invalid data"""
    response = client.post("/send-message",
                           json=get_message(),
                           headers={'authorization': f'Bearer_{valid_token}1'})
    assert response.status_code == 401


def test_send_token_usernames_do_not_match():
    """/send-message the key is valid, but names in the key and message do not match"""
    response = client.post("/send-message",
                           json=get_message(valid_user=False),
                           headers={'authorization': f'Bearer_{valid_token}'})
    assert response.status_code == 401


def test_send_history():
    """/send-message text matches 'history 10' pattern"""
    response = client.post("/send-message",
                           json=get_message(),
                           headers={'authorization': f'Bearer_{valid_token}'})
    assert response.status_code == 200
    assert response.json() == messages


def test_send_no_such_user():
    """/send-message the name of the user from the header does not exist in the DB"""
    response = client.post("/send-message",
                           json=get_message(valid_user=False),
                           headers={'authorization': f'Bearer_{valid_token}'})
    assert response.status_code == 401


def test_send_add_message():
    """/send-message add new message then check contents"""
    new_message = 'new message'

    response = client.post("/send-message",
                           json={'name': name, 'message': new_message},
                           headers={'authorization': f'Bearer_{valid_token}'})
    assert response.status_code == 200

    messages.insert(0, {'message': new_message, 'name': name})
    response = client.post("/send-message",
                           json=get_message(),
                           headers={'authorization': f'Bearer_{valid_token}'})
    assert response.status_code == 200
    assert response.json() == messages
