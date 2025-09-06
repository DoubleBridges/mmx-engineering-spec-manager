from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class ExportResult:
    success: bool
    message: str = ""
    output_paths: List[Path] = field(default_factory=list)


class ProjectExporter(ABC):
    """Abstract exporter for project targets (e.g., Microvellum XML, XLSX)."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def export(self, project: Any, target_dir: Path, options: Dict[str, Any] | None = None) -> ExportResult:
        ...
