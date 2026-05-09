from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentBinding:
    runtime_ref: Optional[str]
    session_ref: Optional[str]
    provider: Optional[str] = None
    runtime_root: Optional[str] = None
    runtime_pid: Optional[int] = None
    session_file: Optional[str] = None
    session_id: Optional[str] = None
    tmux_socket_name: Optional[str] = None
    tmux_socket_path: Optional[str] = None
    terminal: Optional[str] = None
    pane_id: Optional[str] = None
    active_pane_id: Optional[str] = None
    pane_title_marker: Optional[str] = None
    pane_state: Optional[str] = None
    provider_identity_state: Optional[str] = None
    provider_identity_reason: Optional[str] = None


def binding_status(runtime_ref: Optional[str], session_ref: Optional[str], workspace_path: Optional[str]) -> str:
    if runtime_ref and session_ref and workspace_path:
        return 'bound'
    if runtime_ref or session_ref or workspace_path:
        return 'partial'
    return 'unbound'


__all__ = ['AgentBinding', 'binding_status']
