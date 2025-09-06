from __future__ import annotations
import os
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from PySide6.QtCore import QStandardPaths
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


def _app_data_dir() -> str:
    """Return the writable application data directory (matches prior default)."""
    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    # Ensure directory exists
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return data_dir


def default_sqlite_db_path() -> str:
    """Default SQLite file path under the application data directory."""
    return os.path.join(_app_data_dir(), "projects.db")


def get_database_url() -> str:
    """
    Resolve the database URL from environment (.env supported). Falls back to a
    local SQLite file under the application data directory.

    Examples:
    - sqlite:///C:\\path\\to\\projects.db
    - sqlite:///:memory:
    - postgresql+psycopg2://user:pass@host:5432/dbname
    - postgresql://user:pass@host:5432/dbname (sqlalchemy will infer driver)
    """
    url = os.getenv("DATABASE_URL")
    if url and url.strip():
        return url.strip()
    # Default to the previous behavior: sqlite file under AppDataLocation
    db_path = default_sqlite_db_path()
    return f"sqlite:///{db_path}"


def create_engine_and_sessionmaker(echo: bool = False) -> Tuple[object, sessionmaker]:
    """
    Create a SQLAlchemy engine and a bound sessionmaker based on the resolved URL.
    Applies SQLite-specific connect args when needed.
    """
    url = get_database_url()
    connect_args = {}
    if url.startswith("sqlite"):  # apply SQLite recommended connect args
        # For file-based SQLite, ensure parent dir exists
        if url.startswith("sqlite:///") and not url.endswith(":memory:"):
            # Path part after sqlite:/// may have forward slashes; SQLAlchemy handles it.
            # We already ensured app data dir exists; nothing else required here.
            pass
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, echo=echo, connect_args=connect_args)
    Session = sessionmaker(bind=engine)
    return engine, Session
