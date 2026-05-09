from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class RoomValidationError(ValueError):
    pass


class RoomSource(str, Enum):
    CLI = 'cli'
    IMESSAGE = 'imessage'
    SYSTEM = 'system'
    AGENT = 'agent'


class RoomEventType(str, Enum):
    USER_MESSAGE = 'user_message'
    AGENT_MESSAGE = 'agent_message'
    SYSTEM_MESSAGE = 'system_message'
    TASK_SUBMITTED = 'task_submitted'
    TASK_STARTED = 'task_started'
    TASK_COMPLETED = 'task_completed'
    TASK_FAILED = 'task_failed'
    APPROVAL_NEEDED = 'approval_needed'
    STATUS_SNAPSHOT = 'status_snapshot'
    TRANSPORT_DELIVERY = 'transport_delivery'
    TRANSPORT_ERROR = 'transport_error'


@dataclass(slots=True)
class RoomEvent:
    room_id: str
    source: RoomSource
    sender: str
    target: str
    type: RoomEventType
    body: str
    event_id: str = field(default_factory=lambda: f'evt_{uuid4().hex}')
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    correlation_id: str | None = None
    parent_event_id: str | None = None
    job_id: str | None = None
    agent_name: str | None = None
    transport: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.room_id.strip():
            raise RoomValidationError('room_id cannot be empty')

        if not self.sender.strip():
            raise RoomValidationError('sender cannot be empty')

        if not self.target.strip():
            raise RoomValidationError('target cannot be empty')

        if not self.body.strip():
            raise RoomValidationError('body cannot be empty')

    def to_record(self) -> dict[str, Any]:
        return {
            'event_id': self.event_id,
            'room_id': self.room_id,
            'created_at': self.created_at,
            'source': self.source.value,
            'sender': self.sender,
            'target': self.target,
            'type': self.type.value,
            'body': self.body,
            'correlation_id': self.correlation_id,
            'parent_event_id': self.parent_event_id,
            'job_id': self.job_id,
            'agent_name': self.agent_name,
            'transport': self.transport,
            'metadata': self.metadata,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> 'RoomEvent':
        return cls(
            event_id=record['event_id'],
            room_id=record['room_id'],
            created_at=record['created_at'],
            source=RoomSource(record['source']),
            sender=record['sender'],
            target=record['target'],
            type=RoomEventType(record['type']),
            body=record['body'],
            correlation_id=record.get('correlation_id'),
            parent_event_id=record.get('parent_event_id'),
            job_id=record.get('job_id'),
            agent_name=record.get('agent_name'),
            transport=record.get('transport'),
            metadata=record.get('metadata'),
        )
