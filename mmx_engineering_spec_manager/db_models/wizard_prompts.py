from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.prompts_mixin import PromptsMixin


class WizardPrompts(Base, PromptsMixin):
    """
    SQLAlchemy model for the 'wizard_prompts' table.
    """
    __tablename__ = 'wizard_prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    specification_group_id = Column(Integer, ForeignKey('specification_groups.id'), nullable=True)

    project = relationship("Project", back_populates="wizard_prompts")
    specification_group = relationship("SpecificationGroup", back_populates="wizard_prompts")