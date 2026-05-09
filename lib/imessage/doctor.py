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


def run_imessage_doctor() -> IMessageDoctorResult:
    notes: list[str] = []

    platform_supported = platform.system() == 'Darwin'

    if not platform_supported:
        notes.append('iMessage integration currently requires macOS')

    osascript_available = shutil.which('osascript') is not None

    if not osascript_available:
        notes.append('osascript command not found')

    messages_db = Path.home() / 'Library' / 'Messages' / 'chat.db'
    messages_db_exists = messages_db.exists()

    if not messages_db_exists:
        notes.append('Messages chat.db not found')

    notes.append('Inbound iMessage support requires Full Disk Access')

    return IMessageDoctorResult(
        platform_supported=platform_supported,
        osascript_available=osascript_available,
        messages_db_exists=messages_db_exists,
        notes=notes,
    )
