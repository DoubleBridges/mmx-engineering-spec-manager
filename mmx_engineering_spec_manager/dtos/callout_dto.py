from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CalloutDTO:
    """Lightweight DTO for callouts loaded in Attributes tab.

    Fields:
      - type: one of "Finish", "Hardware", "Sink", "Appliance", or "Uncategorized" (singular form)
      - name: display name/material
      - tag: identifier/code
      - description: free text
    """
    type: str
    name: str
    tag: str
    description: str
