import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure PySide6 uses a headless platform in CI environments to avoid aborts
os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

# Provide a lightweight SQLAlchemy session fixture for tests that accept `db_session`
@pytest.fixture
def db_session():
    from mmx_engineering_spec_manager.db_models.database_config import Base
    # Use an in-memory SQLite DB for isolation and speed
    engine = create_engine("sqlite:///:memory:")
    # Create all tables
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        try:
            session.close()
        except Exception:
            pass
        try:
            engine.dispose()
        except Exception:
            pass
