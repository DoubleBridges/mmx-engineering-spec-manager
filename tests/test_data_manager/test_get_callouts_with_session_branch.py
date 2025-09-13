from mmx_engineering_spec_manager.data_manager.manager import DataManager


def test_get_callouts_for_project_with_explicit_session(monkeypatch):
    # Use in-memory DB for the global catalog
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    dm = DataManager()

    # Create a project
    proj = dm.create_or_update_project({
        "number": "COV-TEST-SESSION",
        "name": "Project",
        "job_description": "",
    })

    # Call with explicit session to exercise the 'session is not None' branch
    groups = dm.get_callouts_for_project(proj.id, session=dm.session)
    assert isinstance(groups, dict)
    # Expect empty groups initially
    for k in ("Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized"):
        assert k in groups
