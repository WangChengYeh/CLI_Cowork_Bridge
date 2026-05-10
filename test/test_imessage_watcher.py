from pathlib import Path

from imessage.watcher import (
    IMessageInboundMessage,
    IMessageWatcher,
)
from room.store import RoomEventStore


PARTICIPANTS = {'codex', 'claude', 'gemini', 'pm', 'rd', 'ae'}


def make_message(
    *,
    message_id: int = 1,
    sender_handle: str = '+886912345678',
    text: str = '@codex fix tests',
    is_from_me: bool = False,
):
    return IMessageInboundMessage(
        message_id=message_id,
        chat_id='chat-1',
        sender_handle=sender_handle,
        text=text,
        is_from_me=is_from_me,
    )


def test_accept_valid_message(tmp_path: Path):
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
    assert decision.event.target == 'codex'

    events = store.list_events()

    assert len(events) == 1


def test_reject_non_allowlisted_sender(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886000000000'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(make_message())

    assert decision.accepted is False
    assert 'allowlisted' in decision.reason


def test_reject_missing_prefix(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(
        make_message(text='hello world')
    )

    assert decision.accepted is False
    assert 'prefix' in decision.reason


def test_reject_outgoing_message(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(
        make_message(is_from_me=True)
    )

    assert decision.accepted is False
    assert 'outgoing' in decision.reason


def test_dry_run_does_not_persist(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(
        make_message(),
        dry_run=True,
    )

    assert decision.accepted is True

    events = store.list_events()

    assert len(events) == 0


def test_initialize_cursor_sets_max_id(tmp_path: Path):
    import sqlite3
    db_path = tmp_path / 'chat.db'
    connection = sqlite3.connect(db_path)
    connection.execute('CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT)')
    connection.execute('INSERT INTO message (text) VALUES ("old 1")')
    connection.execute('INSERT INTO message (text) VALUES ("old 2")')
    connection.commit()
    connection.close()

    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    watcher = IMessageWatcher(
        project_root=tmp_path,
        db_path=db_path,
        store=store,
    )

    # Initial state: cursor is 0
    assert watcher.read_cursor() == 0

    # Initialize: should set to max ID (2)
    max_id = watcher.initialize_cursor()
    assert max_id == 2
    assert watcher.read_cursor() == 2

    # Subsequent calls should not change it
    assert watcher.initialize_cursor() == 2
