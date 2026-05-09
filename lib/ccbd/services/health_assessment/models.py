from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPaneAssessment:
    binding: Optional[object]
    session: Optional[object]
    terminal: Optional[str]
    pane_state: Optional[str]
    health: str
