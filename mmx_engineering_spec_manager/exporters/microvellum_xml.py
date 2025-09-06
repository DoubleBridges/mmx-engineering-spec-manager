from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import xml.etree.ElementTree as ET

from .contracts import ProjectExporter, ExportResult
from .registry import register_exporter


class MicrovellumXmlExporter(ProjectExporter):
    """Minimal Microvellum-like XML exporter for MVP/testing.

    Produces a simple XML structure capturing project and product essentials:
    <Project number="..." name="..." job_description="...">
      <Products>
        <Product name="..." quantity="..." width="..." height="..." depth="..."
                 XOrigin="..." YOrigin="..." ZOrigin="..." />
      </Products>
    </Project>
    """

    @property
    def name(self) -> str:
        return "microvellum_xml"

    def export(self, project: Any, target_dir: Path, options: Dict[str, Any] | None = None) -> ExportResult:
        options = options or {}
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = options.get("filename") or f"{getattr(project, 'number', 'project')}.xml"
        out_path = target_dir / filename

        try:
            root = ET.Element(
                "Project",
                attrib={
                    "number": str(getattr(project, "number", "")),
                    "name": str(getattr(project, "name", "")),
                    "job_description": str(getattr(project, "job_description", "")),
                },
            )

            products_parent = ET.SubElement(root, "Products")
            products = getattr(project, "products", []) or []
            for p in products:
                attrs: Dict[str, str] = {
                    "name": str(getattr(p, "name", "")),
                    "quantity": str(getattr(p, "quantity", "") or ""),
                    "width": str(getattr(p, "width", "") or ""),
                    "height": str(getattr(p, "height", "") or ""),
                    "depth": str(getattr(p, "depth", "") or ""),
                }
                # Microvellum origins if available
                xori = getattr(p, "x_origin_from_right", None)
                yori = getattr(p, "y_origin_from_face", None)
                zori = getattr(p, "z_origin_from_bottom", None)
                if xori is not None:
                    attrs["XOrigin"] = str(xori)
                if yori is not None:
                    attrs["YOrigin"] = str(yori)
                if zori is not None:
                    attrs["ZOrigin"] = str(zori)

                ET.SubElement(products_parent, "Product", attrib=attrs)

            tree = ET.ElementTree(root)
            # Write with XML declaration
            tree.write(out_path, encoding="utf-8", xml_declaration=True)

            return ExportResult(success=True, message="Exported Microvellum XML", output_paths=[out_path])
        except Exception as e:
            return ExportResult(success=False, message=f"XML export failed: {e}", output_paths=[])


# Auto-register on import for convenience
register_exporter("microvellum_xml", lambda: MicrovellumXmlExporter())
