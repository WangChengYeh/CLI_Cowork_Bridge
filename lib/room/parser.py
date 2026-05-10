from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


class RoomCommandError(ValueError):
    pass


@dataclass
class ParsedRoomCommand:
    raw_text: str
    command: str
    target: str
    body: str
    is_broadcast: bool = False
    is_status: bool = False


DEFAULT_ALIASES = {
    'code': 'codex',
    'review': 'claude',
    'research': 'gemini',
    'claude': 'pm',
    'codex': 'writer',
    'gemini': 'reviewer',
}


def parse_room_command(
    text: str,
    participants: set[str],
    prefix: str = '@',
    aliases: Optional[dict[str, str]] = None,
) -> ParsedRoomCommand:
    raw = text.strip()

    if not raw:
        raise RoomCommandError('command text cannot be empty')

    if not raw.startswith(prefix):
        raise RoomCommandError(f'command must start with {prefix}')

    aliases_map = dict(DEFAULT_ALIASES)
    if aliases:
        aliases_map.update(aliases)

    without_prefix = raw[len(prefix):].strip()

    if not without_prefix:
        raise RoomCommandError('missing command target')

    parts = without_prefix.split(maxsplit=1)
    target = parts[0].strip().lower()
    body = parts[1].strip() if len(parts) > 1 else ''

    target = aliases_map.get(target, target)

    if target == 'status':
        return ParsedRoomCommand(
            raw_text=raw,
            command='status',
            target='status',
            body='',
            is_status=True,
        )

    if target == 'all':
        if not body:
            raise RoomCommandError('@all requires a message body')

        return ParsedRoomCommand(
            raw_text=raw,
            command='broadcast',
            target='all',
            body=body,
            is_broadcast=True,
        )

    if target not in participants:
        raise RoomCommandError(f'unknown participant: {target}')

    if not body:
        raise RoomCommandError('message body cannot be empty')

    return ParsedRoomCommand(
        raw_text=raw,
        command='message',
        target=target,
        body=body,
    )
