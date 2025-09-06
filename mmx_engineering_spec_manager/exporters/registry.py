from __future__ import annotations
from typing import Callable, Dict, List

from .contracts import ProjectExporter


_exporter_factories: Dict[str, Callable[[], ProjectExporter]] = {}


def register_exporter(name: str, factory: Callable[[], ProjectExporter]) -> None:
    _exporter_factories[name] = factory


def get_exporter(name: str) -> ProjectExporter | None:
    factory = _exporter_factories.get(name)
    return factory() if factory else None


def list_exporter_names() -> List[str]:
    return sorted(_exporter_factories.keys())
