from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from room.models import RoomEvent, RoomEventType
from room.store import RoomEventStore


@dataclass
class RuntimeLoopResult:
    processed_events: int
    next_offset: int


class RuntimeEventLoop:
    def __init__(
        self,
        *,
        project_root: Path,
        store: Optional[RoomEventStore] = None,
        cursor_name: str = 'runtime-supervisor',
        on_event: Callable[[RoomEvent], Optional[None]] = None,
    ) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.cursor_name = cursor_name
        self.on_event = on_event

    def poll_once(self, *, limit: int = 100) -> RuntimeLoopResult:
        events, next_offset = self.store.tail_from_cursor(
            self.cursor_name,
            limit=limit,
        )

        for event in events:
            self._handle_event(event)

        self.store.write_cursor(self.cursor_name, next_offset)

        return RuntimeLoopResult(
            processed_events=len(events),
            next_offset=next_offset,
        )

    def run_forever(self, *, interval_seconds: float = 1.0) -> None:
        while True:
            self.poll_once()
            time.sleep(interval_seconds)

    def _handle_event(self, event: RoomEvent) -> None:
        if self.on_event is not None:
            self.on_event(event)

        if event.type is RoomEventType.USER_MESSAGE:
            self.store.append_audit(
                {
                    'type': 'runtime_user_message_seen',
                    'event_id': event.event_id,
                    'target': event.target,
                }
            )
