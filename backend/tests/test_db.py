from app.db import SessionLocal, get_session_dep, init_db
from app.models.tables import ScenarioModel


def test_init_db_creates_all_tables():
    init_db()
    session = SessionLocal()
    try:
        assert session.query(ScenarioModel).count() == 0
    finally:
        session.close()


def test_get_session_dep_yields_and_closes_session():
    generator = get_session_dep()
    session = next(generator)
    assert session.bind is SessionLocal().bind

    generator_exhausted = False
    try:
        next(generator)
    except StopIteration:
        generator_exhausted = True
    assert generator_exhausted
