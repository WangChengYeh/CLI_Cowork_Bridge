from __future__ import annotations

from typing import Optional

from pathlib import Path

from provider_backends.pane_log_support.session import compute_session_key_for_provider

from .model import OpenCodeProjectSession
from .pathing import find_project_session_file, read_json


def load_project_session(work_dir: Path, instance: Optional[str] = None) -> Optional[OpenCodeProjectSession]:
    session_file = find_project_session_file(work_dir, instance)
    if not session_file:
        return None
    data = read_json(session_file)
    if not data:
        return None
    return OpenCodeProjectSession(session_file=session_file, data=data)


def compute_session_key(session: OpenCodeProjectSession, instance: Optional[str] = None) -> str:
    return compute_session_key_for_provider(session, provider="opencode", instance=instance)


__all__ = ["compute_session_key", "load_project_session"]
