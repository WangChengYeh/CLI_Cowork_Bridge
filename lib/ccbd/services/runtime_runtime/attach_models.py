from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from agents.models import RuntimeBindingSource


@dataclass(frozen=True)
class AttachRuntimeValues:
    backend_type: str
    runtime_ref: Optional[str]
    session_ref: Optional[str]
    workspace_path: str
    state: object
    health: str
    provider: str
    runtime_root: Optional[str]
    runtime_pid: Optional[int]
    terminal_backend: Optional[str]
    pane_id: Optional[str]
    active_pane_id: Optional[str]
    pane_title_marker: Optional[str]
    pane_state: Optional[str]
    tmux_socket_name: Optional[str]
    tmux_socket_path: Optional[str]
    session_file: Optional[str]
    session_id: Optional[str]
    slot_key: Optional[str]
    window_id: Optional[str]
    workspace_epoch: Optional[int]
    lifecycle_state: Optional[str]
    binding_generation: int
    runtime_generation: int
    daemon_generation: Optional[int]
    authority_epoch_changed: bool
    managed_by: str
    binding_source: RuntimeBindingSource


__all__ = ['AttachRuntimeValues']
