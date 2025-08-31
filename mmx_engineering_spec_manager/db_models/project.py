from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base

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
    custom_fields = relationship("CustomField", back_populates="project")
    global_prompts = relationship("GlobalPrompts", back_populates="project")
    wizard_prompts = relationship("WizardPrompts", back_populates="project")
    walls = relationship("Wall", back_populates="project")
    finish_callouts = relationship("FinishCallout", back_populates="project")
    hardware_callouts = relationship("HardwareCallout", back_populates="project")
    sink_callouts = relationship("SinkCallout", back_populates="project")
    appliance_callouts = relationship("ApplianceCallout", back_populates="project")