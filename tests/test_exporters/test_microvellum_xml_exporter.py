from pathlib import Path
import xml.etree.ElementTree as ET

from mmx_engineering_spec_manager.exporters.microvellum_xml import MicrovellumXmlExporter


class _Prod:
    def __init__(self, name="Cabinet", quantity=1, width=30.0, height=34.5, depth=24.0,
                 x_origin_from_right=None, y_origin_from_face=None, z_origin_from_bottom=None):
        self.name = name
        self.quantity = quantity
        self.width = width
        self.height = height
        self.depth = depth
        self.x_origin_from_right = x_origin_from_right
        self.y_origin_from_face = y_origin_from_face
        self.z_origin_from_bottom = z_origin_from_bottom


class _Project:
    def __init__(self):
        self.number = "P-123"
        self.name = "Test Project"
        self.job_description = "JD"
        self.products = [
            _Prod(name="Cab", quantity=2, width=18, height=30, depth=24, x_origin_from_right=10.0, y_origin_from_face=2.0, z_origin_from_bottom=5.0)
        ]


def test_microvellum_xml_exporter_writes_expected_xml(tmp_path: Path):
    proj = _Project()
    exporter = MicrovellumXmlExporter()
    res = exporter.export(proj, tmp_path)
    assert res.success
    assert res.output_paths and res.output_paths[0].exists()

    # Parse and validate XML
    tree = ET.parse(res.output_paths[0])
    root = tree.getroot()
    assert root.tag == "Project"
    assert root.attrib.get("number") == proj.number

    prods = list(root.findall("Products/Product"))
    assert len(prods) == 1
    p = prods[0]
    assert p.attrib.get("name") == "Cab"
    assert p.attrib.get("width") == "18"
    assert p.attrib.get("XOrigin") == "10.0"
    assert p.attrib.get("ZOrigin") == "5.0"
