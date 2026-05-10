from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore
from runtime.workers.dispatch_worker import DispatchWorker


class FakeStreamRD:
    def __init__(self, **kwargs):
        self.calls = []

    def execute(self, request):
        self.calls.append(request)

        class Result:
            output_events = [1, 2]

        return Result()



def make_event() -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
    )


def test_dispatch_worker_executes_user_message(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    worker = DispatchWorker(
        project_root=tmp_path,
        store=store,
        stream_executor_factory=FakeStreamRD,
    )

    event = make_event()
    store.append(event)

    result = worker.handle(event)

    assert result.submitted_event_id is not None
    assert result.streamed_event_count == 2


def test_non_user_message_is_ignored(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    worker = DispatchWorker(
        project_root=tmp_path,
        store=store,
        stream_executor_factory=FakeStreamRD,
    )

    event = RoomEvent(
        room_id='default',
        source=RoomSource.SYSTEM,
        sender='system',
        target='codex',
        type=RoomEventType.TASK_COMPLETED,
        body='done',
    )

    result = worker.handle(event)

    assert result.submitted_event_id is None
    assert result.streamed_event_count == 0
