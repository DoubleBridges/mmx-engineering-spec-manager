from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
# from mmx_engineering_spec_manager.db_models.location import Location # Remove this
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.prompt import Prompt


class Product(Base):
    """
    SQLAlchemy model for the 'products' table.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    quantity = Column(Integer)
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)

    project_id = Column(Integer, ForeignKey('projects.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))

    project = relationship("Project", back_populates="products")
    location = relationship("Location", back_populates="products")
    custom_fields = relationship("CustomField", back_populates="product")
    prompts = relationship("Prompt", back_populates="product")