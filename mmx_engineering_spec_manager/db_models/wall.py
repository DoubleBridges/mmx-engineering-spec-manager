from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base

class Wall(Base):
    """
    SQLAlchemy model for the 'walls' table.
    """
    __tablename__ = 'walls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(String)
    link_id_location = Column(String)
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)
    x_origin = Column(Float)
    y_origin = Column(Float)
    z_origin = Column(Float)
    angle = Column(Float)

    project_id = Column(Integer, ForeignKey('projects.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))

    project = relationship("Project", back_populates="walls")
    location = relationship("Location", back_populates="walls")
    products = relationship("Product", back_populates="wall")