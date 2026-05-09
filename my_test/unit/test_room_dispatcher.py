from pathlib import Path

from room.dispatcher import (
    RoomDispatcher,
    RoomDispatchError,
)
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore



def make_user_event(target: str = 'codex') -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target=target,
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
    )


def test_dispatch_prepare_only_creates_task_submitted(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    source_event = make_user_event()
    store.append(source_event)

    result = dispatcher.dispatch_prepare_only(source_event)

    submitted = result.submitted_event

    assert submitted.type is RoomEventType.TASK_SUBMITTED
    assert submitted.parent_event_id == source_event.event_id
    assert submitted.correlation_id is not None


def test_dispatch_request_generates_ask_argv(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    source_event = make_user_event()

    result = dispatcher.dispatch_prepare_only(source_event)

    argv = result.request.to_ask_argv()

    assert argv[0] == 'ask'
    assert argv[1] == 'codex'
    assert argv[2] == 'fix failing tests'


def test_broadcast_request_rejects_single_argv(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    source_event = make_user_event(target='all')

    result = dispatcher.dispatch_prepare_only(source_event)

    try:
        result.request.to_ask_argv()
    except RoomDispatchError as exc:
        assert 'broadcast' in str(exc)
    else:
        raise AssertionError('expected RoomDispatchError')


def test_non_user_message_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    source_event = RoomEvent(
        room_id='default',
        source=RoomSource.SYSTEM,
        sender='system',
        target='codex',
        type=RoomEventType.TASK_COMPLETED,
        body='done',
    )

    try:
        dispatcher.dispatch_prepare_only(source_event)
    except RoomDispatchError as exc:
        assert 'USER_MESSAGE' in str(exc)
    else:
        raise AssertionError('expected RoomDispatchError')
