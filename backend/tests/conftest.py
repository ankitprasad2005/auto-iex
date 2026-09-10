import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def db_session():
    # Imported lazily so this conftest collects cleanly for tests that don't
    # need the DB fixture, even before app.models exists (Task 10).
    from app.models.base import Base
    import app.models.tables  # noqa: F401  registers all mapped tables

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
