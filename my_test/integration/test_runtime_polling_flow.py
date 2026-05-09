from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore
from runtime.event_loop import RuntimeEventLoop
from runtime.supervisor import RuntimeSupervisor
from runtime.worker import RuntimeWorker



def make_event(index: int) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body=f'fix failing tests {index}',
    )


def test_runtime_polling_flow_preserves_cursor_progression(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=tmp_path,
        store=store,
        event_loop=RuntimeEventLoop(
            project_root=tmp_path,
            store=store,
            cursor_name='runtime-supervisor',
        ),
    )

    received = []

    supervisor.register_worker(
        RuntimeWorker(
            name='collector',
            handler=received.append,
        )
    )

    first = make_event(1)
    second = make_event(2)

    store.append(first)
    store.append(second)

    first_poll = supervisor.poll_once()

    assert first_poll.processed_events == 2
    assert received == [first, second]

    second_poll = supervisor.poll_once()

    assert second_poll.processed_events == 0
    assert received == [first, second]


def test_runtime_polling_flow_processes_new_events_only(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=tmp_path,
        store=store,
        event_loop=RuntimeEventLoop(
            project_root=tmp_path,
            store=store,
            cursor_name='runtime-supervisor',
        ),
    )

    received = []

    supervisor.register_worker(
        RuntimeWorker(
            name='collector',
            handler=received.append,
        )
    )

    first = make_event(1)
    store.append(first)

    supervisor.poll_once()

    second = make_event(2)
    store.append(second)

    second_poll = supervisor.poll_once()

    assert second_poll.processed_events == 1
    assert received[-1] == second
