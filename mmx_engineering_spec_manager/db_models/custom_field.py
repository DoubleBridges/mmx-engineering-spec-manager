from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.parameter import Parameter


class CustomField(Base, Parameter):
    """
    SQLAlchemy model for the 'custom_fields' table.
    """
    __tablename__ = 'custom_fields'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))

    product = relationship("Product", back_populates="custom_fields")