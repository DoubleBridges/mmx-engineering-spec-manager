from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.repositories.unit_of_work import SqlAlchemyUnitOfWork
# Direct import to ensure __init__ executes and symbols are exposed
from mmx_engineering_spec_manager.repositories import ProjectRepository, SqlAlchemyProjectRepository  # noqa: F401
import importlib


def test_repositories_init_imports():
    # Ensure repositories package __init__ executes for coverage (redundant but explicit)
    importlib.import_module('mmx_engineering_spec_manager.repositories')


def test_uow_add_and_get_by_number():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with SqlAlchemyUnitOfWork(Session) as uow:
        assert list(uow.projects.get_all()) == []
        p = Project(number="123", name="Test Project")
        uow.projects.add(p)
        uow.commit()

    with SqlAlchemyUnitOfWork(Session) as uow2:
        proj = uow2.projects.get_by_number("123")
        assert proj is not None
        assert proj.name == "Test Project"


def test_uow_rollback():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with SqlAlchemyUnitOfWork(Session) as uow:
        uow.projects.add(Project(number="999", name="Should Rollback"))
        uow.rollback()

    with SqlAlchemyUnitOfWork(Session) as uow2:
        assert uow2.projects.get_by_number("999") is None


def test_repo_get_by_id_and_update_and_exit_with_exception_rolls_back():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Create a project and commit
    with SqlAlchemyUnitOfWork(Session) as uow:
        p = Project(number="321", name="Alpha")
        uow.projects.add(p)
        uow.commit()
        pid = p.id

    # Read by id and update
    with SqlAlchemyUnitOfWork(Session) as uow2:
        p2 = uow2.projects.get_by_id(pid)
        assert p2 is not None
        p2.name = "Beta"
        uow2.projects.update(p2)
        uow2.commit()

    # Verify update persisted
    with SqlAlchemyUnitOfWork(Session) as uow3:
        p3 = uow3.projects.get_by_id(pid)
        assert p3 is not None and p3.name == "Beta"

    # Now ensure __exit__ rollback path is hit when exception occurs
    try:
        with SqlAlchemyUnitOfWork(Session) as uow4:
            uow4.projects.add(Project(number="777", name="Temp"))
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    # The project added in the failed transaction should not be present
    with SqlAlchemyUnitOfWork(Session) as uow5:
        assert uow5.projects.get_by_number("777") is None
