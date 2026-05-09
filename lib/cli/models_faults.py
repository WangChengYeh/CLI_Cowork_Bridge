from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedFaultListCommand:
    project: Optional[str]
    kind: str = 'fault-list'


@dataclass(frozen=True)
class ParsedFaultArmCommand:
    project: Optional[str]
    agent_name: str
    task_id: str
    reason: str
    count: int
    error_message: str
    kind: str = 'fault-arm'


@dataclass(frozen=True)
class ParsedFaultClearCommand:
    project: Optional[str]
    target: str
    kind: str = 'fault-clear'


__all__ = [
    'ParsedFaultArmCommand',
    'ParsedFaultClearCommand',
    'ParsedFaultListCommand',
]
