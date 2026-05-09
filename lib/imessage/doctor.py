from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class IMessageDoctorResult:
    platform_supported: bool
    osascript_available: bool
    messages_db_exists: bool
    notes: list[str]

    @property
    def ok(self) -> bool:
        return self.platform_supported and self.osascript_available


def run_imessage_doctor(
    *,
    platform_name: str | None = None,
    osascript_available: bool | None = None,
    chat_db_exists: bool | None = None,
) -> IMessageDoctorResult:
    notes: list[str] = []

    detected_platform = platform_name if platform_name is not None else platform.system()
    platform_supported = detected_platform == 'Darwin'

    if not platform_supported:
        notes.append('iMessage integration currently requires macOS')

    detected_osascript = (
        osascript_available
        if osascript_available is not None
        else shutil.which('osascript') is not None
    )

    if not detected_osascript:
        notes.append('osascript command not found')

    if chat_db_exists is None:
        messages_db = Path.home() / 'Library' / 'Messages' / 'chat.db'
        detected_chat_db = messages_db.exists()
    else:
        detected_chat_db = chat_db_exists

    if not detected_chat_db:
        notes.append('Messages chat.db not found')

    notes.append('Inbound iMessage support requires Full Disk Access')

    return IMessageDoctorResult(
        platform_supported=platform_supported,
        osascript_available=detected_osascript,
        messages_db_exists=detected_chat_db,
        notes=notes,
    )
