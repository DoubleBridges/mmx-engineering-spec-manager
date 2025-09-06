from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.services.ingest_innergy_project_service import IngestInnergyProjectService
from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.importers.contracts import ProjectImporter, ProjectSummaryDTO


class _StubImporter(ProjectImporter):
    def __init__(self, project_payload=None, products=None):
        self._project = project_payload or {
            "Number": "P-ING-1",
            "Name": "Ingested Project",
            "JobDescription": "JD",
            "Address": {"Address1": "123 Main"},
            # Provide locations for mapping
            "locations": [{"name": "Kitchen"}, {"name": "Bath"}],
        }
        self._products = products if products is not None else [
            {
                "Name": "Cabinet A",
                "QuantCount": 2,
                "Description": "Desc A",
                "CustomFields": [{"Name": "CF1", "Value": "V1"}],
            },
            {
                "Name": "Cabinet B",
                "QuantCount": 1,
                "Description": "Desc B",
                "CustomFields": [],
            },
        ]

    @property
    def name(self) -> str:
        return "stub"

    def list_projects(self):
        return [ProjectSummaryDTO(id=1, number=self._project.get("Number"), name=self._project.get("Name"), address="123 Main")]

    def fetch_project(self, job_id):
        return self._project

    def fetch_products(self, job_id):
        return list(self._products) if self._products is not None else []


def _build_session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def test_ingest_service_persists_project_locations_products_and_cfs():
    Session = _build_session_factory()
    importer = _StubImporter()
    svc = IngestInnergyProjectService(session_factory=Session, importer=importer)

    res = svc.ingest(job_id="ANY")
    assert res.project is not None
    assert res.project.number == "P-ING-1"
    # Verify project persisted with children using a fresh session
    s = Session()
    try:
        p = s.query(Project).filter_by(number="P-ING-1").first()
        assert p is not None
        # Locations created (2)
        assert len(getattr(p, "locations", [])) == 2
        # Products created (2) and custom fields on first product
        assert len(getattr(p, "products", [])) == 2
        prods = p.products
        cf_total = sum(len(getattr(prod, "custom_fields", [])) for prod in prods)
        assert cf_total == 1
    finally:
        s.close()


def test_ingest_service_update_existing_project_and_skip_duplicate_locations():
    Session = _build_session_factory()
    # First ingest creates project and locations/products
    importer1 = _StubImporter()
    svc = IngestInnergyProjectService(session_factory=Session, importer=importer1)
    svc.ingest(job_id="JOB1")

    # Second ingest with same number but different name should update
    project2 = {
        "Number": "P-ING-1",
        "Name": "Updated Name",
        "JobDescription": "JD2",
        "Address": {"Address1": "456 Oak"},
        # Same locations to exercise skip logic
        "locations": [{"name": "Kitchen"}, {"name": "Bath"}],
    }
    importer2 = _StubImporter(project_payload=project2, products=[])
    res2 = svc.ingest(job_id="JOB2") if False else IngestInnergyProjectService(Session, importer2).ingest("JOB2")

    # Verify name was updated and locations not duplicated
    s = Session()
    try:
        p = s.query(Project).filter_by(number="P-ING-1").first()
        assert p is not None
        assert p.name == "Updated Name"
        assert len(p.locations) == 2
        # products from second ingest were empty; total products should remain 2 from first ingest
        assert len(p.products) == 2
    finally:
        s.close()


def test_ingest_service_handles_no_products_branch():
    Session = _build_session_factory()
    importer = _StubImporter(products=[])
    svc = IngestInnergyProjectService(session_factory=Session, importer=importer)
    res = svc.ingest(job_id="X")
    # No products should be attached
    s = Session()
    try:
        p = s.query(Project).filter_by(number="P-ING-1").first()
        assert p is not None
        assert len(p.products) == 0
    finally:
        s.close()
