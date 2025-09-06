from pathlib import Path
import os

from mmx_engineering_spec_manager.exporters.xlsx_template import XlsxTemplateExporter
from mmx_engineering_spec_manager.utilities import settings as settings_module


def _reset_settings_singleton():
    settings_module._settings_singleton = None  # type: ignore[attr-defined]


class _Project:
    def __init__(self):
        self.number = "P-999"
        self.name = "Proj XLSX"


def test_xlsx_exporter_uses_template_when_available(tmp_path: Path, monkeypatch):
    # Create a fake template file
    template = tmp_path / "tmpl.xlsx"
    template.write_text("TEMPLATE", encoding="utf-8")

    # Point settings to the template
    monkeypatch.setenv("XLSX_TEMPLATE_PATH", str(template))
    _reset_settings_singleton()

    proj = _Project()
    exporter = XlsxTemplateExporter()
    res = exporter.export(proj, tmp_path, options={"filename": "out.xlsx"})
    assert res.success
    assert (tmp_path / "out.xlsx").exists()
    assert (tmp_path / "out.xlsx").read_text(encoding="utf-8") == "TEMPLATE"


def test_xlsx_exporter_creates_placeholder_without_template(tmp_path: Path, monkeypatch):
    # Ensure env is not set
    monkeypatch.delenv("XLSX_TEMPLATE_PATH", raising=False)
    _reset_settings_singleton()

    proj = _Project()
    exporter = XlsxTemplateExporter()
    res = exporter.export(proj, tmp_path)
    assert res.success
    # The exporter chooses default filename based on project.number
    out = tmp_path / f"{proj.number}.xlsx"
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "XLSX placeholder" in txt
