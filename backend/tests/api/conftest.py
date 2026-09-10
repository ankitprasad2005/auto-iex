import pytest
from fastapi.testclient import TestClient

from app.db import get_session_dep
from app.main import app


@pytest.fixture()
def client(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_session_dep] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
