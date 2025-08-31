from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base

class Prompt(Base):
    """
    SQLAlchemy model for the 'prompts' table.
    """
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(String)

    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    specification_group_id = Column(Integer, ForeignKey('specification_groups.id'), nullable=True)
    global_prompts_id = Column(Integer, ForeignKey('global_prompts.id'), nullable=True)
    wizard_prompts_id = Column(Integer, ForeignKey('wizard_prompts.id'), nullable=True)

    parent_id = Column(Integer, ForeignKey('prompts.id'), nullable=True)

    product = relationship("Product", back_populates="prompts")
    specification_group = relationship("SpecificationGroup", back_populates="prompts")
    global_prompts = relationship("GlobalPrompts", back_populates="prompts")
    wizard_prompts = relationship("WizardPrompts", back_populates="prompts")

    parent = relationship("Prompt", remote_side=[id], back_populates="children")
    children = relationship("Prompt", back_populates="parent")