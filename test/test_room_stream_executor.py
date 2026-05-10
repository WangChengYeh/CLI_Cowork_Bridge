from pathlib import Path

from room.dispatcher import RoomDispatchRequest
from room.models import RoomEventType
from room.store import RoomEventStore
from room.stream_executor import RoomAskStreamExecutor


class FakeStdout:
    def __init__(self, lines):
        self._lines = lines

    def __iter__(self):
        return iter(self._lines)


class FakeProcess:
    def __init__(self, lines, returncode=0):
        self.stdout = FakeStdout(lines)
        self._returncode = returncode

    def wait(self):
        return self._returncode


class FakePopen:
    def __init__(self, *, lines, returncode=0):
        self.calls = []
        self.lines = lines
        self.returncode = returncode

    def __call__(self, argv, cwd, stdout, stderr, text):
        self.calls.append(
            {
                'argv': argv,
                'cwd': cwd,
                'stdout': stdout,
                'stderr': stderr,
                'text': text,
            }
        )
        return FakeProcess(self.lines, self.returncode)


def make_request() -> RoomDispatchRequest:
    return RoomDispatchRequest(
        target='codex',
        body='fix failing tests',
        source_event_id='evt_123',
        room_id='default',
        sender='you',
        source='cli',
    )


def test_stream_executor_generates_agent_messages(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    fake_popen = FakePopen(
        lines=[
            'Analyzing failing tests\n',
            'Applying patch\n',
            'Tests now passing\n',
        ],
        returncode=0,
    )

    emitted_events = []

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=fake_popen,
        on_event=emitted_events.append,
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert len(result.output_events) == 3
    assert len(emitted_events) == 4

    events = store.list_events()

    assert events[0].type is RoomEventType.AGENT_MESSAGE
    assert events[1].body == 'Applying patch'
    assert events[-1].type is RoomEventType.TASK_COMPLETED


def test_stream_executor_handles_failure(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    fake_popen = FakePopen(
        lines=['Provider crashed\n'],
        returncode=1,
    )

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=fake_popen,
    )

    result = rd.execute(make_request())

    assert result.returncode == 1
    assert result.terminal_event is not None
    assert result.terminal_event.type is RoomEventType.TASK_FAILED
