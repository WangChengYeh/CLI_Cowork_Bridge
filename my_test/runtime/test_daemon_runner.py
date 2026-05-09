from pathlib import Path

from room.models import RoomEvent, RoomEventType, RoomSource
from runtime.bootstrap import bootstrap_runtime
from runtime.daemon_runner import run_runtime_forever



def test_run_runtime_forever_processes_events(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
    )

    event = RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix tests',
    )

    runtime.store.append(event)

    result = run_runtime_forever(
        project_root=tmp_path,
        bootstrap=runtime,
        max_iterations=1,
        sleep_fn=lambda _: None,
    )

    assert result.iterations == 1
    assert result.processed_events >= 1



def test_run_runtime_forever_updates_daemon_state(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
    )

    result = run_runtime_forever(
        project_root=tmp_path,
        bootstrap=runtime,
        max_iterations=1,
        sleep_fn=lambda _: None,
    )

    state_path = (
        tmp_path / '.ccb' / 'runtime-daemon.json'
    )

    assert state_path.exists()
    assert result.iterations == 1



def test_run_runtime_forever_stops_by_condition(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
    )

    result = run_runtime_forever(
        project_root=tmp_path,
        bootstrap=runtime,
        sleep_fn=lambda _: None,
        should_stop=lambda: True,
    )

    assert result.iterations == 0
    assert result.stopped_by_condition is True
