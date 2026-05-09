from pathlib import Path

from room.dispatcher import RoomDispatchError, RoomDispatcher
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore


def make_user_event(target: str, body: str, *, broadcast: bool = False) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target=target,
        type=RoomEventType.USER_MESSAGE,
        body=body,
        metadata={'is_broadcast': broadcast},
    )


def test_build_dispatch_request(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    event = make_user_event('codex', 'fix tests')

    request = dispatcher.build_request(event)

    assert request.target == 'codex'
    assert request.body == 'fix tests'

    argv = request.to_ask_argv()

    assert argv == ['ask', 'codex', 'fix tests']


def test_dispatch_prepare_only_creates_task_submitted_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    source_event = make_user_event('claude', 'review latest diff')
    store.append(source_event)

    result = dispatcher.dispatch_prepare_only(source_event)

    assert result.submitted_event.type is RoomEventType.TASK_SUBMITTED

    events = store.list_events()

    assert len(events) == 2
    assert events[1].parent_event_id == source_event.event_id


def test_reject_system_dispatch_target(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    event = make_user_event('system', 'status')

    try:
        dispatcher.build_request(event)
    except RoomDispatchError as exc:
        assert 'unsupported dispatch target' in str(exc)
    else:
        raise AssertionError('expected RoomDispatchError')


def test_broadcast_cannot_convert_to_single_argv(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    dispatcher = RoomDispatcher(project_root=tmp_path, store=store)

    event = make_user_event('all', 'sync current state', broadcast=True)

    request = dispatcher.build_request(event)

    try:
        request.to_ask_argv()
    except RoomDispatchError as exc:
        assert 'broadcast events cannot be converted' in str(exc)
    else:
        raise AssertionError('expected RoomDispatchError')
