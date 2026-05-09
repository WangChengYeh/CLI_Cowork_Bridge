from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore
from runtime.supervisor import RuntimeSupervisor
from runtime.worker import RuntimeWorker


def make_event() -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
    )


def test_register_worker(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=tmp_path,
        store=store,
    )

    worker = RuntimeWorker(
        name='worker-1',
        handler=lambda event: None,
    )

    supervisor.register_worker(worker)

    status = supervisor.status()

    assert status.worker_count == 1


def test_poll_once_dispatches_to_workers(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    event = make_event()
    store.append(event)

    seen = []

    supervisor = RuntimeSupervisor(
        project_root=tmp_path,
        store=store,
    )

    supervisor.register_worker(
        RuntimeWorker(
            name='collector',
            handler=seen.append,
        )
    )

    result = supervisor.poll_once()

    assert result.processed_events == 1
    assert len(seen) == 1
    assert seen[0].event_id == event.event_id


def test_status_returns_cursor_name(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=tmp_path,
        store=store,
    )

    status = supervisor.status()

    assert status.cursor_name == 'runtime-supervisor'
