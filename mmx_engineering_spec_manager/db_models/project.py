# mmx_engineering_spec_manager/db_models/project.py
from sqlalchemy import Column, Integer, String
from mmx_engineering_spec_manager.db_models.database_config import Base

class Project(Base):
    """
    SQLAlchemy model for the 'projects' table.
    """
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    name = Column(String)
    job_description = Column(String)