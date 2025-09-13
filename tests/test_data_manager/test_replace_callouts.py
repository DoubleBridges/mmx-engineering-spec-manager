import pytest
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.finish_callout import FinishCallout
from mmx_engineering_spec_manager.db_models.hardware_callout import HardwareCallout
from mmx_engineering_spec_manager.db_models.sink_callout import SinkCallout
from mmx_engineering_spec_manager.db_models.appliance_callout import ApplianceCallout
from mmx_engineering_spec_manager.dtos.callout_dto import CalloutDTO


def test_replace_callouts_for_project(db_session):
    # Arrange a project in the test DB
    p = Project(number="P2", name="Proj2")
    db_session.add(p)
    db_session.commit()

    grouped = {
        "Finishes": [CalloutDTO(type="Finish", name="Lam A", tag="PL1", description="D")],
        "Hardware": [{"name": "Pull", "tag": "HW3", "description": "D"}],
        # Include a sink entry missing tag to exercise continue path
        "Sinks": [{"name": "Sink A", "description": "x"}],
        "Appliances": [CalloutDTO(type="Appliance", name="Microwave", tag="AP1", description="D")],
        "Uncategorized": [{"name": "Unknown", "tag": "ZZ1", "description": "U"}],
    }

    dm = DataManager()
    dm.replace_callouts_for_project(p.id, grouped, session=db_session)

    finishes = db_session.query(FinishCallout).filter_by(project_id=p.id).all()
    hardware = db_session.query(HardwareCallout).filter_by(project_id=p.id).all()
    sinks = db_session.query(SinkCallout).filter_by(project_id=p.id).all()
    appliances = db_session.query(ApplianceCallout).filter_by(project_id=p.id).all()

    assert len(finishes) == 1
    assert finishes[0].material == "Lam A" and finishes[0].tag == "PL1"
    assert len(hardware) == 1
    assert hardware[0].material == "Pull" and hardware[0].tag == "HW3"
    assert len(sinks) == 0
    assert len(appliances) == 1
    assert appliances[0].material == "Microwave" and appliances[0].tag == "AP1"
