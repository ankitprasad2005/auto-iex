import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import get_session_dep
from app.main import app


@pytest.fixture()
def db_session(tmp_path, monkeypatch):
    # Override parent db_session to allow multi-threading (required for TestClient)
    from app.models.base import Base
    import app.models.tables  # noqa: F401  registers all mapped tables
    import app.db

    # Use file-based SQLite instead of in-memory to avoid threading issues
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    Base.metadata.create_all(engine)

    # Also patch app.db.engine so the startup event uses the same database
    monkeypatch.setattr(app.db, "engine", engine)

    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_session_dep] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
