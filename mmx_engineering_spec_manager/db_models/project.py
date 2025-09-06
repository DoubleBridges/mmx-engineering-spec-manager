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
    job_address = Column(String)

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

    @property
    def specification_groups(self):
        """Derived collection of unique SpecificationGroup objects for this project.
        It aggregates the specification_group from each product and returns a
        stable, de-duplicated list. No DB schema change required.
        """
        # Collect unique by id while skipping None
        seen = {}
        for p in (self.products or []):
            sg = getattr(p, "specification_group", None)
            if sg is not None:
                # Prefer id as key when available, else use name tuple to avoid duplicates
                key = getattr(sg, "id", None)
                if key is None:
                    key = (getattr(sg, "name", None), id(sg))
                if key not in seen:
                    seen[key] = sg
        # Deterministic order: by name (case-insensitive) then id
        def sort_key(item):
            sg = item[1]
            name = getattr(sg, "name", "") or ""
            sgid = getattr(sg, "id", 0) or 0
            return (name.lower(), sgid)
        return [sg for _, sg in sorted(seen.items(), key=sort_key)]