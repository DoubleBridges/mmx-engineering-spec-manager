from mmx_engineering_spec_manager.repositories.sqlalchemy_repositories import SqlAlchemyProjectRepository
from mmx_engineering_spec_manager.db_models.project import Project


class _QueryStub:
    def __init__(self, model):
        self.model = model

    def get(self, project_id):
        # Return a dummy project instance to prove this path was used
        p = Project(number="stub", name="Stub")
        p.id = project_id
        return p


class _SessionWithoutGet:
    # No .get attribute on purpose to trigger except path
    def query(self, model):
        return _QueryStub(model)


def test_get_by_id_fallback_to_query_get_when_session_has_no_get():
    repo = SqlAlchemyProjectRepository(_SessionWithoutGet())
    proj = repo.get_by_id(42)
    assert isinstance(proj, Project)
    assert proj.id == 42
