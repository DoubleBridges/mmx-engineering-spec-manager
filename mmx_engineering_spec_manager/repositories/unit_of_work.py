from __future__ import annotations
from typing import Optional, Protocol

from sqlalchemy.orm import sessionmaker, Session

from .interfaces import ProjectRepository
from .sqlalchemy_repositories import SqlAlchemyProjectRepository


class UnitOfWork(Protocol):
    projects: ProjectRepository

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


class SqlAlchemyUnitOfWork:
    """Unit of Work implementation wrapping a SQLAlchemy session factory.

    Usage:
        uow = SqlAlchemyUnitOfWork(session_factory)
        with uow as tx:
            projects = tx.projects.get_all()
            tx.commit()
    """

    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self.projects: ProjectRepository = None  # type: ignore

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        # Keep attributes available after commit; prevents DetachedInstanceError for returned entities
        try:
            self.session.expire_on_commit = False
        except Exception:  # pragma: no cover
            # Some Session implementations may not expose this; ignore
            pass  # pragma: no cover
        self.projects = SqlAlchemyProjectRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is not None:
                self.rollback()
            else:
                # If user forgot to commit, do not auto-commit; just leave it as is.
                pass
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()
