from pathlib import Path

from room.imessage_correlation import (
    IMessageCorrelationError,
    IMessageCorrelationStore,
)
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore


def make_imessage_event() -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.IMESSAGE,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
        transport={
            'name': 'imessage',
            'chat_id': 'chat-1',
            'message_id': 123,
            'sender_handle': '+886912345678',
        },
    )


def test_imessage_event_creates_binding(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    correlation = IMessageCorrelationStore(
        project_root=tmp_path,
        store=store,
    )

    binding = correlation.bind_source_event(
        make_imessage_event(),
        correlation_id='job-123',
    )

    assert binding is not None
    assert binding.chat_id == 'chat-1'
    assert binding.message_id == 123
    assert binding.recipient == '+886912345678'


def test_cli_source_event_returns_none(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    correlation = IMessageCorrelationStore(
        project_root=tmp_path,
        store=store,
    )

    event = RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix tests',
    )

    binding = correlation.bind_source_event(
        event,
        correlation_id='job-456',
    )

    assert binding is None


def test_binding_round_trip(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    correlation = IMessageCorrelationStore(
        project_root=tmp_path,
        store=store,
    )

    correlation.bind_source_event(
        make_imessage_event(),
        correlation_id='job-789',
    )

    loaded = correlation.load_binding('job-789')

    assert loaded is not None
    assert loaded.chat_id == 'chat-1'
    assert loaded.message_id == 123
    assert loaded.recipient == '+886912345678'


def test_invalid_transport_binding_raises(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bindings = store.read_transport_bindings()
    bindings['imessage-correlation:bad'] = {
        'transport': 'not-imessage',
        'correlation_id': 'bad',
        'source_event_id': 'evt_1',
        'recipient': '+886912345678',
    }
    store.write_transport_bindings(bindings)

    correlation = IMessageCorrelationStore(
        project_root=tmp_path,
        store=store,
    )

    try:
        correlation.load_binding('bad')
    except IMessageCorrelationError:
        pass
    else:
        raise AssertionError('expected IMessageCorrelationError')
