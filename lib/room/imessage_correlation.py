from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .models import RoomEvent, RoomSource
from .store import RoomEventStore


class IMessageCorrelationError(RuntimeError):
    pass


@dataclass
class IMessageCorrelationBinding:
    correlation_id: str
    source_event_id: str
    chat_id: Optional[str]
    message_id: Optional[int]
    recipient: str

    def to_record(self) -> dict[str, Any]:
        return {
            'correlation_id': self.correlation_id,
            'source_event_id': self.source_event_id,
            'transport': 'imessage',
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'recipient': self.recipient,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> 'IMessageCorrelationBinding':
        if record.get('transport') != 'imessage':
            raise IMessageCorrelationError('binding transport is not imessage')
        return cls(
            correlation_id=str(record['correlation_id']),
            source_event_id=str(record['source_event_id']),
            chat_id=record.get('chat_id'),
            message_id=record.get('message_id'),
            recipient=str(record['recipient']),
        )


def binding_key(correlation_id: str) -> str:
    return f'imessage-correlation:{correlation_id}'


class IMessageCorrelationStore:
    def __init__(self, *, project_root: Path, store: Optional[RoomEventStore] = None) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')

    def bind_source_event(self, event: RoomEvent, *, correlation_id: str) -> Optional[IMessageCorrelationBinding]:
        if event.source is not RoomSource.IMESSAGE:
            return None

        transport = event.transport or {}
        recipient = str(transport.get('sender_handle') or '').strip()
        if not recipient:
            return None

        binding = IMessageCorrelationBinding(
            correlation_id=correlation_id,
            source_event_id=event.event_id,
            chat_id=transport.get('chat_id'),
            message_id=transport.get('message_id'),
            recipient=recipient,
        )

        bindings = self.store.read_transport_bindings()
        bindings[binding_key(correlation_id)] = binding.to_record()
        self.store.write_transport_bindings(bindings)
        return binding

    def load_binding(self, correlation_id: str) -> Optional[IMessageCorrelationBinding]:
        bindings = self.store.read_transport_bindings()
        record = bindings.get(binding_key(correlation_id))
        if not record:
            return None
        return IMessageCorrelationBinding.from_record(record)
