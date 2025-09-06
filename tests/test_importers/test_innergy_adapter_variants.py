from typing import Iterable

from mmx_engineering_spec_manager.importers.innergy_adapter import InnergyProjectImporterAdapter


class _StubInnergyNone:
    def get_projects(self):
        return []

    def get_job_details(self, job_id):
        return {}

    def get_products(self, job_id):
        return None


class _StubInnergyList:
    def get_projects(self):
        return []

    def get_job_details(self, job_id):
        return {}

    def get_products(self, job_id):
        return [{"Name": "X"}]


class _StubInnergyBad:
    def get_projects(self):
        return []

    def get_job_details(self, job_id):
        return {}

    def get_products(self, job_id):
        # Truthy but not list/dict -> triggers final else branch
        return "invalid-shape"


def test_adapter_name_and_variants_cover_all_branches():
    a1 = InnergyProjectImporterAdapter(_StubInnergyNone())
    assert a1.name == "innergy"
    assert list(a1.fetch_products(1)) == []  # not payload branch

    a2 = InnergyProjectImporterAdapter(_StubInnergyList())
    prods = list(a2.fetch_products(1))
    assert prods and prods[0]["Name"] == "X"  # list branch

    a3 = InnergyProjectImporterAdapter(_StubInnergyBad())
    assert list(a3.fetch_products(1)) == []  # final else branch
