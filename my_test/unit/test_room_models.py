from room.models import (
    RoomEvent,
    RoomEventType,
    RoomSource,
    RoomValidationError,
)



def test_room_event_round_trip_preserves_fields():
    event = RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
        metadata={'key': 'value'},
    )

    record = event.to_record()
    restored = RoomEvent.from_record(record)

    assert restored.event_id == event.event_id
    assert restored.room_id == 'default'
    assert restored.source is RoomSource.CLI
    assert restored.type is RoomEventType.USER_MESSAGE
    assert restored.metadata == {'key': 'value'}


def test_generated_event_id_has_evt_prefix():
    event = RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix tests',
    )

    assert event.event_id.startswith('evt_')


def test_empty_room_id_raises():
    try:
        RoomEvent(
            room_id='',
            source=RoomSource.CLI,
            sender='you',
            target='codex',
            type=RoomEventType.USER_MESSAGE,
            body='fix tests',
        )
    except RoomValidationError:
        pass
    else:
        raise AssertionError('expected RoomValidationError')


def test_empty_body_raises():
    try:
        RoomEvent(
            room_id='default',
            source=RoomSource.CLI,
            sender='you',
            target='codex',
            type=RoomEventType.USER_MESSAGE,
            body='',
        )
    except RoomValidationError:
        pass
    else:
        raise AssertionError('expected RoomValidationError')
