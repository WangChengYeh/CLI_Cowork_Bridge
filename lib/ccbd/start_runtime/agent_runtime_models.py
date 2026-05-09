from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from ccbd.models import CcbdStartupAgentResult


@dataclass(frozen=True)
class StartAgentExecution:
    agent_result: CcbdStartupAgentResult
    actions_taken: tuple[str, ...]
    socket_name: Optional[str]
    runtime_pane_id: Optional[str]
    project_socket_active_pane_id: Optional[str]


@dataclass(frozen=True)
class RuntimeBindingState:
    binding: Optional[object]
    agent_action: str
    actions_taken: tuple[str, ...]
    runtime_ref: Optional[str]
    session_ref: Optional[str]
    health: str
    lifecycle_state: str
    socket_name: Optional[str]
    runtime_pane_id: Optional[str]
    project_socket_active_pane_id: Optional[str]


__all__ = ['RuntimeBindingState', 'StartAgentExecution']
