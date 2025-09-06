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
    # Dimensions: Innergy x=width, y=depth, z=height
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)
    # Position on wall for Microvellum export origins (all optional for MVP)
    # XOrigin: distance from right side of wall to product's rightmost x (we store origin for left pos via helpers)
    x_origin_from_right = Column(Float, nullable=True)
    # YOrigin: distance from wall face (plan view y)
    y_origin_from_face = Column(Float, nullable=True)
    # ZOrigin: distance from bottom of wall (elevation y)
    z_origin_from_bottom = Column(Float, nullable=True)

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