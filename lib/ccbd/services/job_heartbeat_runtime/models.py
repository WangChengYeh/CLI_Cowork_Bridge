from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class HeartbeatTickContext:
    snapshot: Optional[object]
    observed_last_progress_at: str
    now: str
    next_state: object
    decision: object


__all__ = ['HeartbeatTickContext']
