from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore



def make_event(index: int) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body=f'fix test {index}',
    )


def test_store_creates_runtime_layout(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    assert store.base_path.exists()
    assert (store.base_path / 'events.jsonl').exists()
    assert (store.base_path / 'audit.jsonl').exists()
    assert (store.base_path / 'cursors').exists()


def test_append_and_list_round_trip(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    event = make_event(1)
    store.append(event)

    events = store.list_events()

    assert len(events) == 1
    assert events[0].event_id == event.event_id


def test_load_event_by_id(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    event = make_event(1)
    store.append(event)

    loaded = store.load_event(event.event_id)

    assert loaded is not None
    assert loaded.body == 'fix test 1'


def test_cursor_round_trip(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.write_cursor('runtime-supervisor', 42)

    assert store.read_cursor('runtime-supervisor') == 42


def test_tail_from_cursor_returns_expected_events(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    for index in range(5):
        store.append(make_event(index))

    events, next_offset = store.tail_from_cursor(
        'runtime-supervisor',
        limit=2,
    )

    assert len(events) == 2
    assert events[0].body == 'fix test 0'
    assert events[1].body == 'fix test 1'
    assert next_offset > 0


def test_transport_bindings_round_trip(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bindings = {
        'imessage:evt_1': {
            'recipient': '+886912345678',
        }
    }

    store.write_transport_bindings(bindings)

    loaded = store.read_transport_bindings()

    assert loaded == bindings
