from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.callout_mixin import CalloutMixin


class LocationTableCallout(Base, CalloutMixin):
    """
    SQLAlchemy model for location-specific callouts (aka Location Table entries).
    Stores a user-assigned Type along with tag/description from CalloutMixin and
    links to both Project and Location within a project's specific database.
    """
    __tablename__ = 'location_table_callouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    # Explicit type for table rows (e.g., Finish/Hardware/Sink/Appliance/Uncategorized)
    type = Column(String)

    project = relationship("Project", back_populates="location_table_callouts")
    location = relationship("Location", back_populates="location_table_callouts")
