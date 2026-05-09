from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class AskSummary:
    project_id: str
    submission_id: Optional[str]
    jobs: tuple[dict, ...]


__all__ = ['AskSummary']
