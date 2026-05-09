from pathlib import Path

from imessage.sender import IMessageSendResult
from room.imessage_delivery import (
    RoomIMessageDelivery,
    RoomIMessageDeliveryPolicy,
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
        body='streamed reply',
    )


def test_disabled_policy_skips_delivery():
    policy = RoomIMessageDeliveryPolicy(
        enabled=False,
        recipients=['+886912345678'],
    )

    should_deliver, reason = should_deliver_to_imessage(
        make_event(RoomEventType.AGENT_MESSAGE),
        policy,
    )

    assert should_deliver is False
    assert reason == 'imessage delivery disabled'


def test_agent_message_delivery_writes_binding_and_transport_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    sender = FakeSender()
    event = make_event(RoomEventType.AGENT_MESSAGE)
    store.append(event)

    delivery = RoomIMessageDelivery(
        project_root=tmp_path,
        store=store,
        policy=RoomIMessageDeliveryPolicy(
            enabled=True,
            recipients=['+886912345678'],
        ),
        send_fn=sender,
    )

    result = delivery.deliver(event, dry_run=True)

    assert result.delivered is True
    assert len(sender.calls) == 1
    assert sender.calls[0]['dry_run'] is True

    bindings = store.read_transport_bindings()
    assert f'imessage:{event.event_id}' in bindings

    events = store.list_events()
    assert events[-1].type is RoomEventType.TRANSPORT_DELIVERY
    assert events[-1].parent_event_id == event.event_id


def test_delivery_deduplicates_by_event_id(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    sender = FakeSender()
    event = make_event(RoomEventType.AGENT_MESSAGE)
    store.append(event)

    delivery = RoomIMessageDelivery(
        project_root=tmp_path,
        store=store,
        policy=RoomIMessageDeliveryPolicy(
            enabled=True,
            recipients=['+886912345678'],
        ),
        send_fn=sender,
    )

    first = delivery.deliver(event, dry_run=True)
    second = delivery.deliver(event, dry_run=True)

    assert first.delivered is True
    assert second.delivered is False
    assert second.reason == 'already delivered'
    assert len(sender.calls) == 1


def test_multiple_recipients_all_receive_message(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    sender = FakeSender()
    event = make_event(RoomEventType.TASK_FAILED)
    store.append(event)

    delivery = RoomIMessageDelivery(
        project_root=tmp_path,
        store=store,
        policy=RoomIMessageDeliveryPolicy(
            enabled=True,
            recipients=['+886900000001', '+886900000002'],
        ),
        send_fn=sender,
    )

    result = delivery.deliver(event, dry_run=True)

    assert result.delivered is True
    assert [call['recipient'] for call in sender.calls] == [
        '+886900000001',
        '+886900000002',
    ]
