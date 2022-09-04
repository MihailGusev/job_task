from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./user_messages.db"


def get_engine(database_url):
    return create_engine(database_url, connect_args={"check_same_thread": False})


engine = get_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
