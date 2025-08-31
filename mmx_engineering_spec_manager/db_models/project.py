from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product

class Project(Base):
    """
    SQLAlchemy model for the 'projects' table.
    """
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    name = Column(String)
    job_description = Column(String)

    locations = relationship("Location", back_populates="project")
    products = relationship("Product", back_populates="project")