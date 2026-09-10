from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL
from .models.base import Base

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_session_dep():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
