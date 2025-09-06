import os
from sqlalchemy import text
from mmx_engineering_spec_manager.utilities.persistence import get_database_url, create_engine_and_sessionmaker


def test_get_database_url_prefers_env_over_default(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    url = get_database_url()
    assert url == "sqlite:///:memory:"


def test_create_engine_and_sessionmaker_with_memory_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    engine, Session = create_engine_and_sessionmaker()
    # Basic smoke checks
    assert engine is not None
    assert Session is not None
    # Create a session and ensure it can connect
    with engine.connect() as conn:
        result = conn.execute(text("select 1"))
        assert result is not None
