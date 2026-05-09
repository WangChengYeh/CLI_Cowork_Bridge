from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from room.dispatcher import RoomDispatchResult, RoomDispatcher
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore

from .imessage_correlation import IMessageCorrelationBinding, IMessageCorrelationStore


@dataclass(slots=True)
class IMessageDispatchResult:
    source_event: RoomEvent
    dispatch_result: RoomDispatchResult
    correlation_binding: IMessageCorrelationBinding | None


class IMessageDispatchBridge:
    def __init__(
        self,
        *,
        project_root: Path,
        store: RoomEventStore | None = None,
        dispatcher: RoomDispatcher | None = None,
        correlation_store: IMessageCorrelationStore | None = None,
    ) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.dispatcher = dispatcher or RoomDispatcher(
            project_root=project_root,
            store=self.store,
        )
        self.correlation_store = correlation_store or IMessageCorrelationStore(
            project_root=project_root,
            store=self.store,
        )

    def dispatch_event(self, event: RoomEvent) -> IMessageDispatchResult:
        dispatch_result = self.dispatcher.dispatch_prepare_only(event)

        correlation_id = (
            dispatch_result.submitted_event.correlation_id
            or dispatch_result.submitted_event.event_id
        )

        binding = self.correlation_store.bind_source_event(
            event,
            correlation_id=correlation_id,
        )

        return IMessageDispatchResult(
            source_event=event,
            dispatch_result=dispatch_result,
            correlation_binding=binding,
        )

    def create_agent_reply(
        self,
        *,
        correlation_id: str,
        agent_name: str,
        body: str,
    ) -> RoomEvent:
        binding = self.correlation_store.load_binding(correlation_id)

        reply_event = RoomEvent(
            room_id='default',
            source=RoomSource.AGENT,
            sender=agent_name,
            target='you',
            type=RoomEventType.AGENT_MESSAGE,
            body=body,
            correlation_id=correlation_id,
            transport={
                'name': 'imessage',
                'recipient': binding.recipient if binding else None,
                'chat_id': binding.chat_id if binding else None,
                'message_id': binding.message_id if binding else None,
            },
            metadata={
                'reply_transport': 'imessage',
                'has_correlation_binding': binding is not None,
            },
        )

        self.store.append(reply_event)
        return reply_event
