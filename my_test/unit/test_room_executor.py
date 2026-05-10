from pathlib import Path

from room.dispatcher import RoomDispatchRequest
from room.executor import RoomAskExecutor
from room.models import RoomEventType
from room.store import RoomEventStore

from my_test.helpers.fake_process import FakeRun



def make_request() -> RoomDispatchRequest:
    return RoomDispatchRequest(
        target='codex',
        body='fix failing tests',
        source_event_id='evt_123',
        room_id='default',
        sender='you',
        source='cli',
    )


def test_successful_subprocess_returns_completed(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    rd = RoomAskExecutor(
        project_root=tmp_path,
        store=store,
        run_fn=FakeRun(
            returncode=0,
            stdout='tests fixed successfully',
        ),
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert result.event.type is RoomEventType.TASK_COMPLETED
    assert 'tests fixed successfully' in result.event.body


def test_failed_subprocess_returns_failed(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    rd = RoomAskExecutor(
        project_root=tmp_path,
        store=store,
        run_fn=FakeRun(
            returncode=1,
            stderr='provider crashed',
        ),
    )

    result = rd.execute(make_request())

    assert result.returncode == 1
    assert result.event.type is RoomEventType.TASK_FAILED
    assert 'provider crashed' in result.event.body


def test_rd_metadata_contains_process_fields(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    fake_run = FakeRun(
        returncode=0,
        stdout='done',
    )

    rd = RoomAskExecutor(
        project_root=tmp_path,
        store=store,
        run_fn=fake_run,
    )

    result = rd.execute(make_request())

    metadata = result.event.metadata

    assert metadata['returncode'] == 0
    assert metadata['stdout'] == 'done'
    assert 'argv' in metadata

    assert len(fake_run.calls) == 1
    assert fake_run.calls[0]['cwd'] == str(tmp_path)
