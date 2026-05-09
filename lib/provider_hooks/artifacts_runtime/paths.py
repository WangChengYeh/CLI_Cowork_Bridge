from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


def completion_dir_from_session_data(session_data: dict[str, Any]) -> Optional[Path]:
    explicit = str(session_data.get('completion_artifact_dir') or '').strip()
    if explicit:
        return Path(explicit).expanduser()
    runtime_dir = str(session_data.get('runtime_dir') or '').strip()
    if runtime_dir:
        return Path(runtime_dir).expanduser() / 'completion'
    return None


__all__ = ['completion_dir_from_session_data']
