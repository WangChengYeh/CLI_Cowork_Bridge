from __future__ import annotations

from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.parser import parse_room_command
from room.store import RoomEventStore


DEFAULT_ROOM_ID = 'default'
DEFAULT_PARTICIPANTS = {'codex', 'claude', 'gemini'}


def room_store_for_project(project_root: Path) -> RoomEventStore:
    return RoomEventStore(project_root / '.ccb' / 'room')


def send_room_message(
    text: str,
    *,
    project_root: Path,
    participants: set[str] | None = None,
    sender: str = 'you',
    source: RoomSource = RoomSource.CLI,
) -> RoomEvent:
    parsed = parse_room_command(
        text,
        participants=participants or DEFAULT_PARTICIPANTS,
    )

    if parsed.is_status:
        event_type = RoomEventType.STATUS_SNAPSHOT
        target = 'system'
        body = 'status requested'
    else:
        event_type = RoomEventType.USER_MESSAGE
        target = parsed.target
        body = parsed.body

    event = RoomEvent(
        room_id=DEFAULT_ROOM_ID,
        source=source,
        sender=sender,
        target=target,
        type=event_type,
        body=body,
        transport={'name': source.value},
        metadata={
            'raw_text': parsed.raw_text,
            'command': parsed.command,
            'is_broadcast': parsed.is_broadcast,
            'is_status': parsed.is_status,
        },
    )

    return room_store_for_project(project_root).append(event)


def list_room_events(
    *,
    project_root: Path,
    limit: int | None = None,
) -> list[RoomEvent]:
    return room_store_for_project(project_root).list_events(limit=limit)


def format_room_event(event: RoomEvent) -> str:
    return f'[{event.created_at}] {event.source.value}:{event.sender} -> {event.target} {event.type.value}: {event.body}'


def render_room_events(events: list[RoomEvent]) -> str:
    return '\n'.join(format_room_event(event) for event in events)
