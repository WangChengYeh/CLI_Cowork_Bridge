from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass

from .applescript import build_send_imessage_script


class IMessageSendError(RuntimeError):
    pass


@dataclass(slots=True)
class IMessageSendResult:
    recipient: str
    message: str
    success: bool
    dry_run: bool = False
    stdout: str | None = None
    stderr: str | None = None


MAX_CHUNK_SIZE = 4000


def split_imessage_chunks(message: str, *, chunk_size: int = MAX_CHUNK_SIZE) -> list[str]:
    if chunk_size <= 0:
        raise IMessageSendError('chunk_size must be positive')

    if not message:
        return ['']

    return [
        message[index:index + chunk_size]
        for index in range(0, len(message), chunk_size)
    ]


def send_imessage(
    recipient: str,
    message: str,
    *,
    dry_run: bool = False,
) -> list[IMessageSendResult]:
    if not recipient.strip():
        raise IMessageSendError('recipient cannot be empty')

    if not message.strip():
        raise IMessageSendError('message cannot be empty')

    if platform.system() != 'Darwin':
        raise IMessageSendError('iMessage sending requires macOS')

    results: list[IMessageSendResult] = []

    for chunk in split_imessage_chunks(message):
        script = build_send_imessage_script(
            recipient=recipient,
            message=chunk,
        )

        if dry_run:
            results.append(
                IMessageSendResult(
                    recipient=recipient,
                    message=chunk,
                    success=True,
                    dry_run=True,
                )
            )
            continue

        process = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
        )

        success = process.returncode == 0

        result = IMessageSendResult(
            recipient=recipient,
            message=chunk,
            success=success,
            dry_run=False,
            stdout=process.stdout,
            stderr=process.stderr,
        )

        if not success:
            raise IMessageSendError(
                process.stderr.strip() or 'osascript failed'
            )

        results.append(result)

    return results
