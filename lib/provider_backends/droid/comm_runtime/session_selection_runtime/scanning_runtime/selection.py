from __future__ import annotations

from typing import Optional

from pathlib import Path

from .candidates import latest_candidate_any_project, matches_work_dir, top_recent_candidates


def scan_latest_session(reader) -> Optional[Path]:
    for path in top_recent_candidates(reader):
        if matches_work_dir(path, work_dir=reader.work_dir):
            return path
    return None


def scan_latest_session_any_project(reader) -> Optional[Path]:
    return latest_candidate_any_project(reader)


__all__ = ["scan_latest_session", "scan_latest_session_any_project"]
