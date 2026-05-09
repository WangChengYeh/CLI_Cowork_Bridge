from __future__ import annotations

from typing import Optional

from pathlib import Path

from agents.models import AgentRuntime, AgentState, RuntimeBindingSource, normalize_runtime_binding_source


def binding_source_for_attach(
    existing: Optional[AgentRuntime],
    *,
    explicit: str | Optional[RuntimeBindingSource],
) -> RuntimeBindingSource:
    if explicit is not None:
        return normalize_runtime_binding_source(explicit)
    if existing is not None:
        return existing.binding_source
    return RuntimeBindingSource.PROVIDER_SESSION


def health_for_attach(
    existing: Optional[AgentRuntime],
    *,
    explicit: Optional[str],
    binding_source: RuntimeBindingSource,
) -> str:
    normalized = normalized_text(explicit)
    if normalized is not None:
        return normalized
    if existing is None:
        return 'healthy'
    current = normalized_text(existing.health) or 'healthy'
    if binding_source is RuntimeBindingSource.EXTERNAL_ATTACH:
        return 'restored' if current == 'restored' else 'healthy'
    return current


def state_for_attach(existing_state: Optional[AgentState], next_health: str) -> AgentState:
    if next_health in {'healthy', 'restored'}:
        if existing_state in {AgentState.DEGRADED, AgentState.STOPPED, AgentState.FAILED} or existing_state is None:
            return AgentState.IDLE
        return existing_state
    return AgentState.DEGRADED


def terminal_backend_from_runtime_ref(runtime_ref: Optional[str]) -> Optional[str]:
    text = str(runtime_ref or '').strip()
    if ':' not in text:
        return None
    backend, _sep, _rest = text.partition(':')
    backend = backend.strip()
    return backend or None


def pane_id_from_runtime_ref(runtime_ref: Optional[str]) -> Optional[str]:
    text = str(runtime_ref or '').strip()
    if ':' not in text:
        return None
    _backend, _sep, pane_id = text.partition(':')
    pane_id = pane_id.strip()
    return pane_id or None


def normalized_text(value: Optional[str]) -> Optional[str]:
    text = str(value or '').strip()
    return text or None


def resolve_session_fields(
    existing: Optional[AgentRuntime],
    *,
    session_ref: Optional[str],
    session_file: Optional[str],
    session_id: Optional[str],
    session_ref_explicit: bool,
    session_file_explicit: bool,
    session_id_explicit: bool,
) -> Optional[tuple[str], Optional[str], Optional[str]]:
    normalized_session_file = normalized_text(session_file)
    normalized_session_id = normalized_text(session_id)
    normalized_session_ref = normalized_text(session_ref)
    next_session_file = _session_field_value(
        existing,
        field_name='session_file',
        explicit_value=normalized_session_file,
        explicit=session_file_explicit,
    )
    next_session_id = _session_field_value(
        existing,
        field_name='session_id',
        explicit_value=normalized_session_id,
        explicit=session_id_explicit,
    )
    next_session_ref = _session_field_value(
        existing,
        field_name='session_ref',
        explicit_value=normalized_session_ref,
        explicit=session_ref_explicit,
    )
    next_session_file, next_session_id = _clear_implicit_session_fields(
        next_session_file,
        next_session_id,
        session_ref_explicit=session_ref_explicit,
        normalized_session_ref=normalized_session_ref,
        session_file_explicit=session_file_explicit,
        session_id_explicit=session_id_explicit,
    )
    next_session_ref = _derived_session_ref(next_session_ref, session_file=next_session_file, session_id=next_session_id)
    next_session_file = _derived_session_file(next_session_file, session_ref=next_session_ref)
    next_session_id = _derived_session_id(next_session_id, session_ref=next_session_ref)
    return next_session_file, next_session_id, next_session_ref


def looks_like_path(value: Optional[str]) -> bool:
    text = str(value or '').strip()
    return bool(text) and (text.startswith('/') or text.startswith('~') or '/' in text or '\\' in text)


def _session_field_value(
    existing: Optional[AgentRuntime],
    *,
    field_name: str,
    explicit_value: Optional[str],
    explicit: bool,
) -> Optional[str]:
    if explicit:
        return explicit_value
    if existing is None:
        return None
    return getattr(existing, field_name)


def _clear_implicit_session_fields(
    session_file: Optional[str],
    session_id: Optional[str],
    *,
    session_ref_explicit: bool,
    normalized_session_ref: Optional[str],
    session_file_explicit: bool,
    session_id_explicit: bool,
) -> Optional[tuple[str], Optional[str]]:
    if not session_ref_explicit or normalized_session_ref is not None:
        return session_file, session_id
    next_session_file = session_file if session_file_explicit else None
    next_session_id = session_id if session_id_explicit else None
    return next_session_file, next_session_id


def _derived_session_ref(
    session_ref: Optional[str],
    *,
    session_file: Optional[str],
    session_id: Optional[str],
) -> Optional[str]:
    return session_ref or session_file or session_id


def _derived_session_file(session_file: Optional[str], *, session_ref: Optional[str]) -> Optional[str]:
    if session_file is not None or not looks_like_path(session_ref):
        return session_file
    return session_ref


def _derived_session_id(session_id: Optional[str], *, session_ref: Optional[str]) -> Optional[str]:
    if session_id is not None or session_ref is None or looks_like_path(session_ref):
        return session_id
    return session_ref


def coerce_pid(value: object) -> Optional[int]:
    text = str(value or '').strip()
    if not text.isdigit():
        return None
    pid = int(text)
    return pid if pid > 0 else None


def read_pid_file(path: Path) -> Optional[int]:
    if not path.is_file():
        return None
    try:
        return coerce_pid(path.read_text(encoding='utf-8'))
    except Exception:
        return None


__all__ = [
    'binding_source_for_attach',
    'coerce_pid',
    'health_for_attach',
    'normalized_text',
    'pane_id_from_runtime_ref',
    'read_pid_file',
    'resolve_session_fields',
    'state_for_attach',
    'terminal_backend_from_runtime_ref',
]
