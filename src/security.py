from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError

SECRET_KEY = 'a7d1e72ffcf7e2cacf55475059201c0347866dbbcee24a8441f17bc3b41a68dd'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """Returns true if hashed plain_password is equal to hashed_password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str):
    """Creates new JWT token"""
    to_encode = {
        'name': username,
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_name_from_token(token: str):
    """Returns name of the user in case if token is valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    else:
        return payload.get('name', None)
