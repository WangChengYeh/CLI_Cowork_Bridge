from pathlib import Path
from subprocess import CompletedProcess

from room.dispatcher import RoomDispatchRequest
from room.executor import RoomAskExecutor
from room.models import RoomEventType
from room.store import RoomEventStore


class FakeRun:
    def __init__(self, *, returncode: int, stdout: str = '', stderr: str = '') -> None:
        self.calls = []
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, argv, cwd, capture_output, text):
        self.calls.append(
            {
                'argv': argv,
                'cwd': cwd,
                'capture_output': capture_output,
                'text': text,
            }
        )
        return CompletedProcess(
            args=argv,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def make_request() -> RoomDispatchRequest:
    return RoomDispatchRequest(
        target='codex',
        body='fix failing tests',
        source_event_id='evt_123',
        room_id='default',
        sender='you',
        source='cli',
    )


def test_execute_success(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    fake_run = FakeRun(returncode=0, stdout='task completed')

    rd = RoomAskExecutor(
        project_root=tmp_path,
        store=store,
        run_fn=fake_run,
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert result.event.type is RoomEventType.TASK_COMPLETED
    assert 'task completed' in result.event.body

    assert len(fake_run.calls) == 1
    assert 'ask' in fake_run.calls[0]['argv']


def test_execute_failure(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    fake_run = FakeRun(returncode=1, stderr='provider failed')

    rd = RoomAskExecutor(
        project_root=tmp_path,
        store=store,
        run_fn=fake_run,
    )

    result = rd.execute(make_request())

    assert result.returncode == 1
    assert result.event.type is RoomEventType.TASK_FAILED
    assert 'provider failed' in result.event.body
