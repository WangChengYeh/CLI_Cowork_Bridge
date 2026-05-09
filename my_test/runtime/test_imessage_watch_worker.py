from room.models import RoomEvent, RoomEventType, RoomSource
from runtime.workers.imessage_watch_worker import IMessageWatchWorker


class Decision:
    def __init__(self, accepted: bool):
        self.accepted = accepted


class FakeWatcher:
    def __init__(self, decisions):
        self.decisions = decisions
        self.calls = []

    def poll_once(self, dry_run=False):
        self.calls.append(
            {
                'dry_run': dry_run,
            }
        )
        return self.decisions



def make_system_event(target: str = 'imessage-watch') -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.SYSTEM,
        sender='system',
        target=target,
        type=RoomEventType.SYSTEM_MESSAGE,
        body='poll watcher',
    )


def test_watch_worker_polls_watcher():
    watcher = FakeWatcher(
        decisions=[
            Decision(True),
            Decision(False),
            Decision(True),
        ]
    )

    worker = IMessageWatchWorker(
        watcher=watcher,
        dry_run=True,
    )

    result = worker.handle(make_system_event())

    assert result.accepted == 2
    assert result.rejected == 1
    assert watcher.calls[0]['dry_run'] is True


def test_non_system_message_is_ignored():
    watcher = FakeWatcher([])

    worker = IMessageWatchWorker(
        watcher=watcher,
    )

    event = RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix tests',
    )

    result = worker.handle(event)

    assert result.accepted == 0
    assert result.rejected == 0
    assert watcher.calls == []


def test_non_watch_target_is_ignored():
    watcher = FakeWatcher([])

    worker = IMessageWatchWorker(
        watcher=watcher,
    )

    result = worker.handle(
        make_system_event(target='other-target')
    )

    assert result.accepted == 0
    assert result.rejected == 0
    assert watcher.calls == []
