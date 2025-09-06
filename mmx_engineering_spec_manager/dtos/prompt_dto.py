from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class PromptDTO:
    """
    Minimal prompt DTO placeholder for MVP. In the future this can be expanded
    to include type information, default values, scope, etc.
    """
    name: str
    value: Optional[Any] = None
