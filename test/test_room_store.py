from pathlib import Path

from lib.room.models import RoomEvent, RoomEventType, RoomSource
from lib.room.store import RoomEventStore


def make_event(body: str) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body=body,
    )


def test_append_and_load_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    event = make_event('fix build error')
    store.append(event)

    loaded = store.load_event(event.event_id)

    assert loaded is not None
    assert loaded.body == 'fix build error'


def test_list_events_limit(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.append(make_event('one'))
    store.append(make_event('two'))
    store.append(make_event('three'))

    events = store.list_events(limit=2)

    assert len(events) == 2
    assert events[0].body == 'two'
    assert events[1].body == 'three'


def test_cursor_tail(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    store.append(make_event('first'))
    store.append(make_event('second'))

    events, next_offset = store.tail_from_cursor('cli')

    assert len(events) == 2
    assert next_offset == 2

    store.write_cursor('cli', next_offset)

    store.append(make_event('third'))

    next_events, next_cursor = store.tail_from_cursor('cli')

    assert len(next_events) == 1
    assert next_events[0].body == 'third'
    assert next_cursor == 3


def test_transport_bindings_roundtrip(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bindings = {
        'job_123': {
            'transport': 'imessage',
            'recipient': '+886912345678',
        }
    }

    store.write_transport_bindings(bindings)

    loaded = store.read_transport_bindings()

    assert loaded['job_123']['transport'] == 'imessage'
