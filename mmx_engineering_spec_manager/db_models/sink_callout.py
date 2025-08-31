from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.callout_mixin import CalloutMixin


class SinkCallout(Base, CalloutMixin):
    """
    SQLAlchemy model for the 'sink_callouts' table.
    """
    __tablename__ = 'sink_callouts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(Integer, ForeignKey('projects.id'))
    specification_group_id = Column(Integer, ForeignKey('specification_groups.id'), nullable=True)

    project = relationship("Project", back_populates="sink_callouts")
    specification_group = relationship("SpecificationGroup", back_populates="sink_callouts")