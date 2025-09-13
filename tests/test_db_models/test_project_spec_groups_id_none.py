from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup


def test_project_specification_groups_id_none_branch(db_session):
    # Create project and specification groups but do not commit them first to keep ids None at access time
    p = Project(number="P3", name="Proj3")
    sg1 = SpecificationGroup(name="Gamma")
    sg2 = SpecificationGroup(name="Alpha")

    # Attach products with these sg objects (ids None until commit)
    prod1 = Product(name="X", project=p, specification_group=sg1)
    prod2 = Product(name="Y", project=p, specification_group=sg2)

    # Add to session but DO NOT flush before accessing property to exercise id None path
    db_session.add_all([p, sg1, sg2, prod1, prod2])

    # Access property which should use the (name, id(sg)) key path
    sgs = p.specification_groups
    names = [sg.name for sg in sgs]
    assert sorted(names, key=str.lower) == sorted(["Alpha", "Gamma"], key=str.lower)
