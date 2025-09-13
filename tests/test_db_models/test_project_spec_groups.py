import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup


def test_project_specification_groups_unique_and_sorted(db_session):
    # Create project
    p = Project(number="P1", name="Proj")

    sg1 = SpecificationGroup(name="Beta")
    sg2 = SpecificationGroup(name="alpha")

    # Products: two with sg1, one with sg2, one without sg
    prod1 = Product(name="A", project=p, specification_group=sg1)
    prod2 = Product(name="B", project=p, specification_group=sg1)
    prod3 = Product(name="C", project=p, specification_group=sg2)
    prod4 = Product(name="D", project=p)  # no group

    db_session.add_all([p, sg1, sg2, prod1, prod2, prod3, prod4])
    db_session.commit()

    # Refresh from DB and compute property
    proj = db_session.query(Project).filter_by(number="P1").first()
    sgs = proj.specification_groups

    # Unique and sorted by name (case-insensitive) then id
    assert [sg.name for sg in sgs] == ["alpha", "Beta"]
    # Ensure duplicates collapsed
    assert len(sgs) == 2
