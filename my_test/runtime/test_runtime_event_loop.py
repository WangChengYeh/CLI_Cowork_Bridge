from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore
from runtime.event_loop import RuntimeEventLoop


def make_event(index: int) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body=f'fix test {index}',
    )


def test_poll_once_consumes_events(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.append(make_event(1))
    store.append(make_event(2))

    seen = []

    loop = RuntimeEventLoop(
        project_root=tmp_path,
        store=store,
        on_event=seen.append,
    )

    result = loop.poll_once()

    assert result.processed_events == 2
    assert len(seen) == 2
    assert seen[0].body == 'fix test 1'
    assert seen[1].body == 'fix test 2'


def test_poll_once_updates_cursor(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.append(make_event(1))

    loop = RuntimeEventLoop(
        project_root=tmp_path,
        store=store,
    )

    result = loop.poll_once()

    cursor = store.read_cursor('runtime-supervisor')

    assert result.next_offset == cursor
    assert cursor > 0


def test_second_poll_does_not_reconsume_events(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.append(make_event(1))

    seen = []

    loop = RuntimeEventLoop(
        project_root=tmp_path,
        store=store,
        on_event=seen.append,
    )

    first = loop.poll_once()
    second = loop.poll_once()

    assert first.processed_events == 1
    assert second.processed_events == 0
    assert len(seen) == 1


def test_limit_restricts_processed_events(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    for index in range(5):
        store.append(make_event(index))

    loop = RuntimeEventLoop(
        project_root=tmp_path,
        store=store,
    )

    result = loop.poll_once(limit=2)

    assert result.processed_events == 2
