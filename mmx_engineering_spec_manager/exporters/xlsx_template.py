from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import shutil

from .contracts import ProjectExporter, ExportResult
from .registry import register_exporter
from mmx_engineering_spec_manager.utilities.settings import get_settings


class XlsxTemplateExporter(ProjectExporter):
    """Exporter that writes an XLSX file based on a template if configured.

    For MVP/testing, if no template is set or missing, we create a simple
    placeholder .xlsx file containing a short message.
    """

    @property
    def name(self) -> str:
        return "xlsx_template"

    def export(self, project: Any, target_dir: Path, options: Dict[str, Any] | None = None) -> ExportResult:
        options = options or {}
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = options.get("filename") or f"{getattr(project, 'number', 'project')}.xlsx"
        out_path = target_dir / filename

        try:
            settings = get_settings()
            tmpl_path = settings.xlsx_template_path
            if tmpl_path and Path(tmpl_path).exists():
                shutil.copyfile(tmpl_path, out_path)
            else:
                # Create a simple placeholder .xlsx (not a valid workbook, but sufficient for tests/MVP)
                out_path.write_text(
                    f"XLSX placeholder for project {getattr(project, 'number', '')}: {getattr(project, 'name', '')}",
                    encoding="utf-8",
                )
            return ExportResult(success=True, message="Exported XLSX (template or placeholder)", output_paths=[out_path])
        except Exception as e:
            return ExportResult(success=False, message=f"XLSX export failed: {e}", output_paths=[])


# Auto-register
register_exporter("xlsx_template", lambda: XlsxTemplateExporter())
