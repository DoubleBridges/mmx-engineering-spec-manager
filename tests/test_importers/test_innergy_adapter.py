from typing import Any, Iterable

from mmx_engineering_spec_manager.importers.innergy_adapter import InnergyProjectImporterAdapter
from mmx_engineering_spec_manager.importers.contracts import ProjectSummaryDTO


class _StubInnergy:
    def __init__(self, projects=None, project=None, products=None):
        self._projects = projects or {
            "Items": [
                {"Id": 1, "Number": "P-100", "Name": "Proj 100", "Address": "Addr 100"},
                {"Id": 2, "Number": "P-200", "Name": "Proj 200", "Address": "Addr 200"},
            ]
        }
        self._project = project or {"Number": "P-100", "Name": "Proj 100", "JobDescription": "JD"}
        self._products = products or {
            "Items": [
                {"Name": "Cabinet", "QuantCount": 3, "Description": "Desc", "CustomFields": [{"Name": "CF1", "Value": "V1"}]}
            ]
        }

    def get_projects(self):
        # Adapter expects already filtered list; mirror current InnergyImporter return shape
        items = self._projects.get("Items", [])
        return [
            {"Id": it.get("Id"), "Number": it.get("Number"), "Name": it.get("Name"), "Address": it.get("Address")}
            for it in items
        ]

    def get_job_details(self, job_id):
        return self._project

    def get_products(self, job_id):
        return self._products


def test_adapter_list_and_fetch():
    adapter = InnergyProjectImporterAdapter(_StubInnergy())
    summaries: Iterable[ProjectSummaryDTO] = adapter.list_projects()
    summaries = list(summaries)
    assert len(summaries) == 2
    assert summaries[0].number == "P-100"
    proj = adapter.fetch_project(1)
    assert proj.get("Number") == "P-100"
    products = list(adapter.fetch_products(1))
    assert products and products[0]["Name"] == "Cabinet"
