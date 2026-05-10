from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from imessage.sender import IMessageSendResult, send_imessage

from .models import RoomEvent, RoomEventType, RoomSource
from .store import RoomEventStore


class RoomIMessageDeliveryError(RuntimeError):
    pass


@dataclass
class RoomIMessageDeliveryPolicy:
    enabled: bool = False
    recipients: list[str] = field(default_factory=list)
    notify_on: set[RoomEventType] = field(
        default_factory=lambda: {
            RoomEventType.AGENT_MESSAGE,
            RoomEventType.TASK_COMPLETED,
            RoomEventType.TASK_FAILED,
            RoomEventType.APPROVAL_NEEDED,
        }
    )
    mirror_cli_inputs: bool = False


@dataclass
class RoomIMessageDeliveryResult:
    event: RoomEvent
    delivered: bool
    reason: Optional[str] = None
    send_results: list[IMessageSendResult] = field(default_factory=list)


def should_deliver_to_imessage(event: RoomEvent, policy: RoomIMessageDeliveryPolicy) -> tuple[bool, Optional[str]]:
    if not policy.enabled:
        return False, 'imessage delivery disabled'

    if not policy.recipients:
        return False, 'no imessage recipients configured'

    if event.type not in policy.notify_on:
        if not (
            policy.mirror_cli_inputs
            and event.source is RoomSource.CLI
            and event.type is RoomEventType.USER_MESSAGE
        ):
            return False, f'event type not configured for delivery: {event.type.value}'

    return True, None


def format_event_for_imessage(event: RoomEvent) -> str:
    return f'[{event.type.value}] {event.sender} → {event.target}\n{event.body}'


class RoomIMessageDelivery:
    def __init__(
        self,
        *,
        project_root: Path,
        policy: RoomIMessageDeliveryPolicy,
        store: Optional[RoomEventStore] = None,
        send_fn: Callable[..., list[IMessageSendResult]] = send_imessage,
    ) -> None:
        self.project_root = project_root
        self.policy = policy
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.send_fn = send_fn

    def deliver(self, event: RoomEvent, *, dry_run: bool = False) -> RoomIMessageDeliveryResult:
        should_deliver, reason = should_deliver_to_imessage(event, self.policy)
        if not should_deliver:
            return RoomIMessageDeliveryResult(event=event, delivered=False, reason=reason)

        bindings = self.store.read_transport_bindings()
        delivered_key = f'imessage:{event.event_id}'

        if bindings.get(delivered_key):
            return RoomIMessageDeliveryResult(event=event, delivered=False, reason='already delivered')

        message = format_event_for_imessage(event)
        send_results: list[IMessageSendResult] = []

        for recipient in self.policy.recipients:
            send_results.extend(
                self.send_fn(
                    recipient=recipient,
                    message=message,
                    dry_run=dry_run,
                )
            )

        bindings[delivered_key] = {
            'event_id': event.event_id,
            'transport': 'imessage',
            'recipients': list(self.policy.recipients),
            'dry_run': dry_run,
        }
        self.store.write_transport_bindings(bindings)

        delivery_event = RoomEvent(
            room_id=event.room_id,
            source=RoomSource.SYSTEM,
            sender='imessage-delivery',
            target='imessage',
            type=RoomEventType.TRANSPORT_DELIVERY,
            body=f'delivered event {event.event_id} to imessage',
            parent_event_id=event.event_id,
            metadata={
                'event_id': event.event_id,
                'recipients': list(self.policy.recipients),
                'dry_run': dry_run,
            },
        )
        self.store.append(delivery_event)

        return RoomIMessageDeliveryResult(
            event=event,
            delivered=True,
            send_results=send_results,
        )
