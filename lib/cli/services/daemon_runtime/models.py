from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from ccbd.services.project_inspection import ProjectDaemonInspection
from ..tmux_project_cleanup import ProjectTmuxCleanupSummary


class CcbdServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class DaemonHandle:
    client: Optional[object]
    inspection: object
    started: bool = False


@dataclass(frozen=True)
class LocalPingSummary:
    project_id: str
    mount_state: str
    desired_state: str
    health: str
    generation: Optional[int]
    project_anchor_path: Optional[str]
    runtime_state_root: Optional[str]
    runtime_root_kind: Optional[str]
    runtime_relocation_reason: Optional[str]
    runtime_filesystem_hint: Optional[str]
    runtime_marker_status: Optional[str]
    socket_path: Optional[str]
    preferred_socket_path: Optional[str]
    effective_socket_path: Optional[str]
    socket_root_kind: Optional[str]
    socket_fallback_reason: Optional[str]
    socket_filesystem_hint: Optional[str]
    tmux_socket_path: Optional[str]
    tmux_preferred_socket_path: Optional[str]
    tmux_effective_socket_path: Optional[str]
    tmux_socket_root_kind: Optional[str]
    tmux_socket_fallback_reason: Optional[str]
    tmux_socket_filesystem_hint: Optional[str]
    last_heartbeat_at: Optional[str]
    pid_alive: bool
    socket_connectable: bool
    heartbeat_fresh: bool
    takeover_allowed: bool
    reason: str
    startup_id: Optional[str] = None
    startup_stage: Optional[str] = None
    last_progress_at: Optional[str] = None
    startup_deadline_at: Optional[str] = None
    last_failure_reason: Optional[str] = None
    shutdown_intent: Optional[str] = None


@dataclass(frozen=True)
class KillSummary:
    project_id: str
    state: str
    socket_path: str
    forced: bool
    cleanup_summaries: tuple[ProjectTmuxCleanupSummary, ...] = ()
    worktree_warnings: tuple[object, ...] = ()


__all__ = [
    'CcbdServiceError',
    'DaemonHandle',
    'KillSummary',
    'LocalPingSummary',
    'ProjectDaemonInspection',
]
