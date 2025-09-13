import os
from pathlib import Path

from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.utilities.persistence import project_sqlite_db_path


def test_per_project_db_roundtrip_callouts(monkeypatch):
    # Use in-memory DB for the global catalog to avoid file writes
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    dm = DataManager()

    # Create a dummy project in the global DB
    proj = dm.create_or_update_project({
        "number": "COV-TEST-001",
        "name": "Coverage Project",
        "job_description": "",
    })
    pid = proj.id

    # Ensure per-project DB path and clean up any existing test artifacts
    db_path = project_sqlite_db_path(proj)
    try:
        Path(db_path).unlink(missing_ok=True)
    except Exception:
        pass

    # Prepare grouped callouts to save (dicts accepted by DataManager)
    grouped = {
        "Finishes": [{"Name": "Lam A", "Tag": "PL1", "Description": "D"}],
        "Hardware": [{"Name": "Pull", "Tag": "HW1", "Description": "D"}],
        "Sinks": [],
        "Appliances": [],
        "Uncategorized": [],
    }

    # Save into per-project DB (no session passed to force per-project branch)
    dm.replace_callouts_for_project(pid, grouped)

    # Read back via per-project DB
    out = dm.get_callouts_for_project(pid)

    assert isinstance(out, dict)
    assert len(out.get("Finishes", [])) == 1
    assert len(out.get("Hardware", [])) == 1

    # Verify a couple of values
    fin = out["Finishes"][0]
    assert fin["Name"] == "Lam A"
    assert fin["Tag"] == "PL1"

    # Clean up the per-project SQLite file created by the test
    try:
        Path(db_path).unlink(missing_ok=True)
    except Exception:
        pass
