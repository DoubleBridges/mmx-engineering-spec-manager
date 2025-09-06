from pathlib import Path
import xml.etree.ElementTree as ET
import shutil
import types

from mmx_engineering_spec_manager.exporters.microvellum_xml import MicrovellumXmlExporter
from mmx_engineering_spec_manager.exporters.xlsx_template import XlsxTemplateExporter
from mmx_engineering_spec_manager.utilities import settings as settings_module


class _Project:
    def __init__(self):
        self.number = "P-FAIL"
        self.name = "Proj"
        self.job_description = ""
        self.products = []


def test_microvellum_xml_exporter_failure(monkeypatch, tmp_path: Path):
    proj = _Project()
    exp = MicrovellumXmlExporter()

    # Monkeypatch ElementTree.ElementTree.write to raise
    class _BadTree(ET.ElementTree):
        def write(self, *args, **kwargs):
            raise RuntimeError("write-fail")

    monkeypatch.setattr(ET, 'ElementTree', _BadTree)

    res = exp.export(proj, tmp_path)
    assert not res.success
    assert "failed" in res.message.lower()


def _reset_settings_singleton():
    settings_module._settings_singleton = None  # type: ignore[attr-defined]


def test_xlsx_template_exporter_failure(monkeypatch, tmp_path: Path):
    # Create a template file
    tmpl = tmp_path / "tmpl.xlsx"
    tmpl.write_text("T", encoding="utf-8")

    # Make shutil.copyfile raise
    monkeypatch.setattr(shutil, 'copyfile', lambda src, dst: (_ for _ in ()).throw(RuntimeError("copy-fail")))

    # Point settings to template
    monkeypatch.setenv("XLSX_TEMPLATE_PATH", str(tmpl))
    _reset_settings_singleton()

    proj = _Project()
    exp = XlsxTemplateExporter()
    res = exp.export(proj, tmp_path)
    assert not res.success
    assert "failed" in res.message.lower()
