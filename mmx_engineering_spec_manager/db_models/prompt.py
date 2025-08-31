from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.parameter import Parameter


class Prompt(Base, Parameter):
    """
    SQLAlchemy model for the 'prompts' table.
    """
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    specification_group_id = Column(Integer, ForeignKey('specification_groups.id'), nullable=True)

    product = relationship("Product", back_populates="prompts")
    specification_group = relationship("SpecificationGroup", back_populates="prompts")