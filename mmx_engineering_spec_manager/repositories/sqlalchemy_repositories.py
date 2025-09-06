from __future__ import annotations
from typing import Iterable, Optional, Any

from sqlalchemy.orm import Session

from mmx_engineering_spec_manager.db_models.project import Project
from .interfaces import ProjectRepository


class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> Iterable[Project]:
        return self.session.query(Project).all()

    def get_by_id(self, project_id: int) -> Optional[Project]:
        # SQLAlchemy 2.0 prefers Session.get
        try:
            return self.session.get(Project, project_id)
        except AttributeError:
            return self.session.query(Project).get(project_id)

    def get_by_number(self, number: str) -> Optional[Project]:
        return self.session.query(Project).filter_by(number=number).first()

    def add(self, project: Project) -> None:
        self.session.add(project)

    def update(self, project: Project) -> None:
        # No-op for SQLAlchemy; committing the session persists changes
        pass
