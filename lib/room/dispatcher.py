from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import RoomEvent, RoomEventType, RoomSource
from .store import RoomEventStore


class RoomDispatchError(RuntimeError):
    pass


@dataclass(slots=True)
class RoomDispatchRequest:
    target: str
    body: str
    source_event_id: str
    room_id: str
    sender: str
    source: str
    is_broadcast: bool = False

    def to_ask_argv(self) -> list[str]:
        if self.is_broadcast:
            raise RoomDispatchError('broadcast events cannot be converted to a single ask argv')
        return ['ask', self.target, self.body]


@dataclass(slots=True)
class RoomDispatchResult:
    request: RoomDispatchRequest
    submitted_event: RoomEvent


class RoomDispatcher:
    def __init__(self, *, project_root: Path, store: RoomEventStore | None = None) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')

    def build_request(self, event: RoomEvent) -> RoomDispatchRequest:
        if event.type is not RoomEventType.USER_MESSAGE:
            raise RoomDispatchError(f'unsupported event type for dispatch: {event.type.value}')

        is_broadcast = bool((event.metadata or {}).get('is_broadcast')) or event.target == 'all'

        if not is_broadcast and event.target in {'system', 'status'}:
            raise RoomDispatchError(f'unsupported dispatch target: {event.target}')

        return RoomDispatchRequest(
            target=event.target,
            body=event.body,
            source_event_id=event.event_id,
            room_id=event.room_id,
            sender=event.sender,
            source=event.source.value,
            is_broadcast=is_broadcast,
        )

    def mark_submitted(self, request: RoomDispatchRequest, *, job_id: str | None = None) -> RoomDispatchResult:
        submitted = RoomEvent(
            room_id=request.room_id,
            source=RoomSource.SYSTEM,
            sender='room-dispatcher',
            target=request.target,
            type=RoomEventType.TASK_SUBMITTED,
            body=f'submitted task to {request.target}',
            parent_event_id=request.source_event_id,
            job_id=job_id,
            correlation_id=job_id or request.source_event_id,
            metadata={
                'source_event_id': request.source_event_id,
                'is_broadcast': request.is_broadcast,
                'source': request.source,
            },
        )
        self.store.append(submitted)
        return RoomDispatchResult(request=request, submitted_event=submitted)

    def dispatch_prepare_only(self, event: RoomEvent) -> RoomDispatchResult:
        request = self.build_request(event)
        return self.mark_submitted(request)
