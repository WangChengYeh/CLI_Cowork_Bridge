from pathlib import Path

from room.dispatcher import RoomDispatchRequest
from room.imessage_delivery import (
    RoomIMessageDelivery,
    RoomIMessageDeliveryPolicy,
)
from room.models import RoomEvent
from room.store import RoomEventStore
from room.stream_executor import RoomAskStreamExecutor

from my_test.helpers.fake_process import FakePopen


class FakeDelivery:
    def __init__(self) -> None:
        self.events = []

    def deliver(self, event: RoomEvent):
        self.events.append(event)
        return None


def make_request() -> RoomDispatchRequest:
    return RoomDispatchRequest(
        target='codex',
        body='fix failing tests',
        source_event_id='evt_123',
        room_id='default',
        sender='you',
        source='cli',
    )


def test_stream_output_is_forwarded_to_delivery_callback(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    fake_delivery = FakeDelivery()

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=[
                'Analyzing issue\n',
                'Applying patch\n',
                'Tests passing\n',
            ],
            returncode=0,
        ),
        on_event=fake_delivery.deliver,
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert len(fake_delivery.events) == 4

    assert fake_delivery.events[0].body == 'Analyzing issue'
    assert fake_delivery.events[1].body == 'Applying patch'
    assert fake_delivery.events[2].body == 'Tests passing'
    assert fake_delivery.events[-1].type.name == 'TASK_COMPLETED'


def test_failed_stream_produces_failed_terminal_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    fake_delivery = FakeDelivery()

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=['Provider crashed\\n'],
            returncode=1,
        ),
        on_event=fake_delivery.deliver,
    )

    result = rd.execute(make_request())

    assert result.returncode == 1
    assert fake_delivery.events[-1].type.name == 'TASK_FAILED'
