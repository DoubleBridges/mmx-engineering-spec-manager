from mmx_engineering_spec_manager.exporters.registry import get_exporter
# Import modules to trigger auto-registration
from mmx_engineering_spec_manager.exporters import microvellum_xml, xlsx_template  # noqa: F401


def test_registered_exporters_are_retrievable():
    xml = get_exporter("microvellum_xml")
    xlsx = get_exporter("xlsx_template")
    assert xml is not None and xml.name == "microvellum_xml"
    assert xlsx is not None and xlsx.name == "xlsx_template"
