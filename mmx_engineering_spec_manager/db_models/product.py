from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base

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
    wall_id = Column(Integer, ForeignKey('walls.id'), nullable=True)
    specification_group_id = Column(Integer, ForeignKey('specification_groups.id'), nullable=True)

    project = relationship("Project", back_populates="products")
    location = relationship("Location", back_populates="products")
    custom_fields = relationship("CustomField", back_populates="product")
    prompts = relationship("Prompt", back_populates="product")
    wall = relationship("Wall", back_populates="products")
    specification_group = relationship("SpecificationGroup", back_populates="products")