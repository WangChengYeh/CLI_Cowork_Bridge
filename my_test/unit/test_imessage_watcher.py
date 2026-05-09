from pathlib import Path

from imessage.watcher import IMessageInboundMessage, IMessageWatcher
from room.store import RoomEventStore


PARTICIPANTS = {'codex', 'claude', 'gemini'}


def make_message(
    *,
    message_id: int = 1,
    sender_handle: str = '+886912345678',
    text: str = '@codex fix failing tests',
    is_from_me: bool = False,
) -> IMessageInboundMessage:
    return IMessageInboundMessage(
        message_id=message_id,
        chat_id='chat-1',
        sender_handle=sender_handle,
        text=text,
        is_from_me=is_from_me,
    )


def make_watcher(tmp_path: Path, store: RoomEventStore) -> IMessageWatcher:
    return IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )


def test_valid_allowlisted_command_becomes_room_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(make_message())

    assert decision.accepted is True
    assert decision.event is not None
    assert decision.event.target == 'codex'
    assert decision.event.transport['message_id'] == 1

    events = store.list_events()
    assert len(events) == 1
    assert events[0].body == 'fix failing tests'


def test_outgoing_message_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(make_message(is_from_me=True))

    assert decision.accepted is False
    assert decision.reason == 'outgoing message ignored'


def test_non_allowlisted_sender_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(
        make_message(sender_handle='+886900000000')
    )

    assert decision.accepted is False
    assert decision.reason == 'sender not allowlisted'


def test_missing_prefix_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(
        make_message(text='hello world')
    )

    assert decision.accepted is False
    assert decision.reason == 'prefix not matched'


def test_dry_run_does_not_append_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(
        make_message(),
        dry_run=True,
    )

    assert decision.accepted is True
    assert store.list_events() == []


def test_status_command_maps_to_system_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = make_watcher(tmp_path, store)

    decision = watcher.evaluate_message(
        make_message(text='@status')
    )

    assert decision.accepted is True
    assert decision.event is not None
    assert decision.event.target == 'system'
    assert decision.event.body == 'status requested'
