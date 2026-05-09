from __future__ import annotations

from typing import Optional

from agents.models import AgentRuntime, RuntimeBindingSource

from .attach_records import new_runtime, should_update_existing, updated_runtime
from .attach_values import resolve_attach_runtime_values


def attach_runtime(
    *,
    registry,
    project_id: str,
    clock,
    agent_name: str,
    workspace_path: str,
    backend_type: str,
    pid: Optional[int] = None,
    runtime_ref: Optional[str] = None,
    session_ref: Optional[str] = None,
    health: Optional[str] = None,
    provider: Optional[str] = None,
    runtime_root: Optional[str] = None,
    runtime_pid: Optional[int] = None,
    terminal_backend: Optional[str] = None,
    pane_id: Optional[str] = None,
    active_pane_id: Optional[str] = None,
    pane_title_marker: Optional[str] = None,
    pane_state: Optional[str] = None,
    tmux_socket_name: Optional[str] = None,
    tmux_socket_path: Optional[str] = None,
    session_file: Optional[str] = None,
    session_id: Optional[str] = None,
    slot_key: Optional[str] = None,
    window_id: Optional[str] = None,
    workspace_epoch: Optional[int] = None,
    lifecycle_state: Optional[str] = None,
    daemon_generation: Optional[int] = None,
    managed_by: Optional[str] = None,
    binding_source: str | Optional[RuntimeBindingSource] = None,
) -> AgentRuntime:
    spec = registry.spec_for(agent_name)
    existing = registry.get(agent_name)
    timestamp = clock()
    values = resolve_attach_runtime_values(
        existing=existing,
        spec=spec,
        workspace_path=workspace_path,
        backend_type=backend_type,
        pid=pid,
        runtime_ref=runtime_ref,
        session_ref=session_ref,
        health=health,
        provider=provider,
        runtime_root=runtime_root,
        runtime_pid=runtime_pid,
        terminal_backend=terminal_backend,
        pane_id=pane_id,
        active_pane_id=active_pane_id,
        pane_title_marker=pane_title_marker,
        pane_state=pane_state,
        tmux_socket_name=tmux_socket_name,
        tmux_socket_path=tmux_socket_path,
        session_file=session_file,
        session_id=session_id,
        slot_key=slot_key,
        window_id=window_id,
        workspace_epoch=workspace_epoch,
        lifecycle_state=lifecycle_state,
        daemon_generation=daemon_generation,
        managed_by=managed_by,
        binding_source=binding_source,
    )

    if should_update_existing(existing):
        updated = updated_runtime(
            existing,
            values=values,
            timestamp=timestamp,
            project_id=project_id,
        )
        return _upsert_authority(registry, updated)

    runtime = new_runtime(
        spec_name=spec.name,
        existing=existing,
        values=values,
        timestamp=timestamp,
        project_id=project_id,
    )
    return _upsert_authority(registry, runtime)


def _upsert_authority(registry, runtime):
    upsert_authority = getattr(registry, 'upsert_authority', None)
    if callable(upsert_authority):
        return upsert_authority(runtime)
    return registry.upsert(runtime)
