from pathlib import Path
from typing import Any, Dict

from mmx_engineering_spec_manager.exporters.contracts import ProjectExporter, ExportResult
from mmx_engineering_spec_manager.exporters.registry import register_exporter, get_exporter, list_exporter_names


class _DummyExporter(ProjectExporter):
    @property
    def name(self) -> str:
        return "dummy_exporter"

    def export(self, project: Any, target_dir: Path, options: Dict[str, Any] | None = None) -> ExportResult:
        return ExportResult(success=True, message="ok", output_paths=[target_dir / "out.xml"]) 


def test_exporter_registry_register_get_list_and_export_result():
    register_exporter("dummy_exporter", lambda: _DummyExporter())
    exp = get_exporter("dummy_exporter")
    assert isinstance(exp, _DummyExporter)
    names = list_exporter_names()
    assert "dummy_exporter" in names

    # Verify ExportResult dataclass usage
    res = exp.export(project=None, target_dir=Path("/tmp"))
    assert res.success is True
    assert "ok" in res.message
    assert res.output_paths and isinstance(res.output_paths[0], Path)
