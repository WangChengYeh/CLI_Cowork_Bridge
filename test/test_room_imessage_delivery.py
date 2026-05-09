from pathlib import Path

from imessage.sender import IMessageSendResult
from room.imessage_delivery import (
    RoomIMessageDelivery,
    RoomIMessageDeliveryPolicy,
    format_event_for_imessage,
    should_deliver_to_imessage,
)
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore


class FakeSender:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, *, recipient: str, message: str, dry_run: bool = False):
        self.calls.append(
            {
                'recipient': recipient,
                'message': message,
                'dry_run': dry_run,
            }
        )
        return [
            IMessageSendResult(
                recipient=recipient,
                message=message,
                success=True,
                dry_run=dry_run,
            )
        ]


def make_event(event_type: RoomEventType) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.AGENT,
        sender='codex',
        target='you',
        type=event_type,
        body='build completed successfully',
    )


def test_should_deliver_to_imessage():
    policy = RoomIMessageDeliveryPolicy(
        enabled=True,
        recipients=['+886912345678'],
    )

    event = make_event(RoomEventType.AGENT_MESSAGE)

    should_deliver, reason = should_deliver_to_imessage(event, policy)

    assert should_deliver is True
    assert reason is None


def test_format_event_for_imessage():
    event = make_event(RoomEventType.TASK_FAILED)

    formatted = format_event_for_imessage(event)

    assert 'task_failed' in formatted
    assert 'build completed successfully' in formatted


def test_delivery_creates_transport_binding(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    sender = FakeSender()

    policy = RoomIMessageDeliveryPolicy(
        enabled=True,
        recipients=['+886912345678'],
    )

    delivery = RoomIMessageDelivery(
        project_root=tmp_path,
        policy=policy,
        store=store,
        send_fn=sender,
    )

    event = make_event(RoomEventType.AGENT_MESSAGE)
    store.append(event)

    result = delivery.deliver(event, dry_run=True)

    assert result.delivered is True
    assert len(sender.calls) == 1

    bindings = store.read_transport_bindings()

    assert f'imessage:{event.event_id}' in bindings


def test_delivery_deduplicates(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    sender = FakeSender()

    policy = RoomIMessageDeliveryPolicy(
        enabled=True,
        recipients=['+886912345678'],
    )

    delivery = RoomIMessageDelivery(
        project_root=tmp_path,
        policy=policy,
        store=store,
        send_fn=sender,
    )

    event = make_event(RoomEventType.AGENT_MESSAGE)
    store.append(event)

    first = delivery.deliver(event, dry_run=True)
    second = delivery.deliver(event, dry_run=True)

    assert first.delivered is True
    assert second.delivered is False
    assert second.reason == 'already delivered'

    assert len(sender.calls) == 1
