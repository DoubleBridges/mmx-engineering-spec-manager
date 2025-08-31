from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base


class SpecificationGroup(Base):
    """
    SQLAlchemy model for the 'specification_groups' table.
    """
    __tablename__ = 'specification_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    prompts = relationship("Prompt", back_populates="specification_group")
    global_prompts = relationship("GlobalPrompts", back_populates="specification_group")
    wizard_prompts = relationship("WizardPrompts", back_populates="specification_group")
    finish_callouts = relationship("FinishCallout", back_populates="specification_group")
    hardware_callouts = relationship("HardwareCallout", back_populates="specification_group")
    sink_callouts = relationship("SinkCallout", back_populates="specification_group")
    appliance_callouts = relationship("ApplianceCallout", back_populates="specification_group")