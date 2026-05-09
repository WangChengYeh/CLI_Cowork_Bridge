from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import RoomEvent


class RoomStoreError(RuntimeError):
    pass


@dataclass(slots=True)
class RoomEventStore:
    root: Path

    @property
    def events_path(self) -> Path:
        return self.root / 'events.jsonl'

    @property
    def cursors_dir(self) -> Path:
        return self.root / 'cursors'

    @property
    def audit_path(self) -> Path:
        return self.root / 'audit.jsonl'

    @property
    def transport_bindings_path(self) -> Path:
        return self.root / 'transport-bindings.json'

    def ensure_layout(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.cursors_dir.mkdir(parents=True, exist_ok=True)
        self.events_path.touch(exist_ok=True)
        self.audit_path.touch(exist_ok=True)
        if not self.transport_bindings_path.exists():
            self.transport_bindings_path.write_text('{}\n', encoding='utf-8')

    def append(self, event: RoomEvent) -> RoomEvent:
        self.ensure_layout()
        with self.events_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event.to_record(), ensure_ascii=False, sort_keys=True))
            handle.write('\n')
        return event

    def iter_events(self) -> Iterable[RoomEvent]:
        self.ensure_layout()
        with self.events_path.open('r', encoding='utf-8') as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield RoomEvent.from_record(json.loads(line))
                except Exception as exc:
                    self.append_audit(
                        {
                            'type': 'corrupt_event_line',
                            'line_number': line_number,
                            'error': str(exc),
                        }
                    )
                    continue

    def list_events(self, *, limit: int | None = None) -> list[RoomEvent]:
        events = list(self.iter_events())
        if limit is None:
            return events
        if limit < 0:
            raise RoomStoreError('limit cannot be negative')
        return events[-limit:]

    def load_event(self, event_id: str) -> RoomEvent | None:
        for event in self.iter_events():
            if event.event_id == event_id:
                return event
        return None

    def read_cursor(self, name: str) -> int:
        path = self._cursor_path(name)
        if not path.exists():
            return 0
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
            return int(payload.get('offset', 0))
        except Exception as exc:
            raise RoomStoreError(f'invalid cursor {name}: {exc}') from exc

    def write_cursor(self, name: str, offset: int) -> None:
        if offset < 0:
            raise RoomStoreError('cursor offset cannot be negative')
        self.ensure_layout()
        self._cursor_path(name).write_text(
            json.dumps({'offset': offset}, ensure_ascii=False, sort_keys=True) + '\n',
            encoding='utf-8',
        )

    def tail_from_cursor(self, name: str, *, limit: int | None = None) -> tuple[list[RoomEvent], int]:
        offset = self.read_cursor(name)
        events = self.list_events()
        selected = events[offset:]
        if limit is not None:
            if limit < 0:
                raise RoomStoreError('limit cannot be negative')
            selected = selected[:limit]
        next_offset = offset + len(selected)
        return selected, next_offset

    def append_audit(self, record: dict[str, object]) -> None:
        self.ensure_layout()
        with self.audit_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write('\n')

    def read_transport_bindings(self) -> dict[str, object]:
        self.ensure_layout()
        try:
            return json.loads(self.transport_bindings_path.read_text(encoding='utf-8') or '{}')
        except Exception as exc:
            raise RoomStoreError(f'invalid transport bindings: {exc}') from exc

    def write_transport_bindings(self, bindings: dict[str, object]) -> None:
        self.ensure_layout()
        self.transport_bindings_path.write_text(
            json.dumps(bindings, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
            encoding='utf-8',
        )

    def _cursor_path(self, name: str) -> Path:
        safe_name = name.strip()
        if not safe_name or '/' in safe_name or '\\' in safe_name:
            raise RoomStoreError('invalid cursor name')
        return self.cursors_dir / f'{safe_name}.json'
