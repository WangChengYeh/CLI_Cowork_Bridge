from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from provider_core.protocol import (
    ANY_DONE_LINE_RE,
    DONE_PREFIX,
    REQ_ID_PREFIX,
    is_done_text,
    make_req_id,
    strip_done_text,
)

from .protocol_runtime import extract_reply_for_req, wrap_droid_prompt


@dataclass(frozen=True)
class DroidRequest:
    client_id: str
    work_dir: str
    timeout_s: float
    quiet: bool
    message: str
    req_id: Optional[str] = None
    caller: str = "claude"


@dataclass(frozen=True)
class DroidResult:
    exit_code: int
    reply: str
    req_id: str
    session_key: str
    done_seen: bool
    done_ms: Optional[int] = None
    anchor_seen: bool = False
    fallback_scan: bool = False
    anchor_ms: Optional[int] = None


__all__ = [
    "ANY_DONE_LINE_RE",
    "DONE_PREFIX",
    "DroidRequest",
    "DroidResult",
    "REQ_ID_PREFIX",
    "extract_reply_for_req",
    "is_done_text",
    "make_req_id",
    "strip_done_text",
    "wrap_droid_prompt",
]
