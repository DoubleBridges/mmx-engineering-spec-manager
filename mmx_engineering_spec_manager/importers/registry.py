from __future__ import annotations
from typing import Callable, Dict, List

from .contracts import ProjectImporter


# Simple in-memory registry for importer plugins
_importer_factories: Dict[str, Callable[[], ProjectImporter]] = {}


def register_importer(name: str, factory: Callable[[], ProjectImporter]) -> None:
    _importer_factories[name] = factory


def get_importer(name: str) -> ProjectImporter | None:
    factory = _importer_factories.get(name)
    return factory() if factory else None


def list_importer_names() -> List[str]:
    return sorted(_importer_factories.keys())
