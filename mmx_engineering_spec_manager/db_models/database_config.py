from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

def get_engine(db_path):
    """
    Returns a SQLAlchemy engine for the given database path.
    """
    DATABASE_URL = f"sqlite:///{db_path}"
    return create_engine(DATABASE_URL)

Base = declarative_base()