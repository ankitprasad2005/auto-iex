import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_session():
    # Imported lazily so this conftest collects cleanly for tests that don't
    # need the DB fixture, even before app.models exists (Task 10).
    from app.models.base import Base
    import app.models.tables  # noqa: F401  registers all mapped tables

    # check_same_thread=False: FastAPI's TestClient runs sync endpoints in a
    # threadpool, so the session must be usable outside the thread that
    # created it. StaticPool keeps the single in-memory connection alive
    # across threads instead of each new connection getting a fresh (empty)
    # in-memory database.
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
