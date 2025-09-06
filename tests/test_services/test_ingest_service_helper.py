from mmx_engineering_spec_manager.services.ingest_innergy_project_service import build_default_ingest_service, IngestInnergyProjectService


def test_build_default_ingest_service_smoke():
    svc = build_default_ingest_service()
    assert isinstance(svc, IngestInnergyProjectService)
