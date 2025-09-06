from unittest.mock import Mock
import requests

from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_get_projects_includes_active_dict_status_and_excludes_inactive(monkeypatch):
    payload = {
        "Items": [
            {
                "Id": "1",
                "Number": "A-1",
                "Name": "Active Dict",
                "Address": "X",
                "Status": {"Name": "Active"},
            },
            {
                "Id": "2",
                "Number": "B-2",
                "Name": "Inactive Dict",
                "Address": "Y",
                "Status": {"Name": "Archived"},
            },
        ]
    }
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = payload
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: resp)

    imp = InnergyImporter()
    projects = imp.get_projects()
    assert len(projects) == 1
    assert projects[0]["Number"] == "A-1"
