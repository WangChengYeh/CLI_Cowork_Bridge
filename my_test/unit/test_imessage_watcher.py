from pathlib import Path

from imessage.watcher import IMessageInboundMessage, IMessageWatcher
from room.store import RoomEventStore


PARTICIPANTS = {'pm', 'rd', 'ae', 'it', 'test_agent'}


def make_message(
    *,
    message_id: int = 1,
    sender_handle: str = '+886912345678',
    text: str = '@rd fix tests',
    is_from_me: bool = False,
):
    return IMessageInboundMessage(
        message_id=message_id,
        chat_id='chat-1',
        sender_handle=sender_handle,
        text=text,
        is_from_me=is_from_me,
    )


def test_valid_allowlisted_command_becomes_room_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(make_message())

    assert decision.accepted is True
    assert decision.event is not None
    assert decision.event.target == 'rd'
    assert decision.event.transport['message_id'] == 1

    events = store.list_events()
    assert len(events) == 1
    assert events[0].body == 'fix tests'


def test_unknown_sender_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886999999999'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(make_message())

    assert decision.accepted is False
    assert decision.reason == 'sender not allowlisted'


def test_unknown_participant_is_rejected(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(
        make_message(text='@unknown do work')
    )

    assert decision.accepted is False
    assert 'unknown participant' in decision.reason


def test_status_command_is_accepted(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(
        make_message(text='@status')
    )

    assert decision.accepted is True
    assert decision.event is not None
    assert decision.event.target == 'system'
    assert decision.event.metadata['is_status'] is True
