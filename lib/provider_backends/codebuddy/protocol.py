"""
CodeBuddy protocol helpers.

Wraps prompts with CCB markers and extracts replies — simplified version
without skills injection.
"""
from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from provider_core.protocol import (
    is_done_text,
    make_req_id,
)

from .protocol_runtime import extract_reply_for_req, wrap_codebuddy_prompt


@dataclass(frozen=True)
class CodeBuddyRequest:
    client_id: str
    work_dir: str
    timeout_s: float
    quiet: bool
    message: str
    req_id: Optional[str] = None
    caller: str = "claude"


@dataclass(frozen=True)
class CodeBuddyResult:
    exit_code: int
    reply: str
    req_id: str
    session_key: str
    done_seen: bool
    done_ms: Optional[int] = None
    anchor_seen: bool = False
    fallback_scan: bool = False
    anchor_ms: Optional[int] = None
