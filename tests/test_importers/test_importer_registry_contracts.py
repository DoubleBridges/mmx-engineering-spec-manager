from dataclasses import dataclass
from typing import Any, Iterable

from mmx_engineering_spec_manager.importers.contracts import ProjectImporter, ProjectSummaryDTO
from mmx_engineering_spec_manager.importers.registry import register_importer, get_importer, list_importer_names


class _DummyImporter(ProjectImporter):
    @property
    def name(self) -> str:
        return "dummy"

    def list_projects(self) -> Iterable[ProjectSummaryDTO]:
        return [ProjectSummaryDTO(id=1, number="P-001", name="Proj", address="Addr")]

    def fetch_project(self, job_id: Any) -> dict:
        return {"Number": "P-001"}

    # Intentionally do not override fetch_products to exercise default returning None


def test_project_importer_default_fetch_products_returns_none():
    imp = _DummyImporter()
    assert imp.fetch_products(job_id=123) is None


def test_importer_registry_register_get_list():
    register_importer("dummy", lambda: _DummyImporter())
    imp = get_importer("dummy")
    assert isinstance(imp, _DummyImporter)
    names = list_importer_names()
    assert "dummy" in names
