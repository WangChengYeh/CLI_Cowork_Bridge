from __future__ import annotations

from typing import Optional

from dataclasses import dataclass
from pathlib import Path

from ..home_layout import current_claude_projects_root

CLAUDE_PROJECTS_ROOT = current_claude_projects_root()


@dataclass
class ClaudeSessionResolution:
    data: dict
    session_file: Optional[Path]
    registry: Optional[dict]
    source: str


__all__ = ["CLAUDE_PROJECTS_ROOT", "ClaudeSessionResolution", "current_claude_projects_root"]
