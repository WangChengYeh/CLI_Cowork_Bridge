from pathlib import Path
import pytest

from runtime.background import launch_background_daemon
from runtime.daemon_state import RuntimeDaemonStateStore
from runtime.watchdog import (
    run_watchdog_loop,
    run_watchdog_tick,
)


@pytest.fixture
def mock_pid_exists(monkeypatch):
    # Mock os.kill to return successfully so pid_exists returns True
    monkeypatch.setattr('os.kill', lambda pid, signum: None)


class FakeProcess:
    def __init__(self, pid: int):
        self.pid = pid


class FakePopen:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append(
            {
                'argv': argv,
                'kwargs': kwargs,
            }
        )

        return FakeProcess(pid=9999)



def test_watchdog_tick_skips_healthy_runtime(tmp_path: Path, mock_pid_exists):
    fake_popen = FakePopen()

    launch_background_daemon(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    result = run_watchdog_tick(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    assert result.runtime_state in {
        'running',
        'stale',
    }
    assert result.restarted is False



def test_watchdog_tick_restarts_stopped_runtime(tmp_path: Path):
    fake_popen = FakePopen()

    result = run_watchdog_tick(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    assert result.runtime_state == 'stopped'
    assert result.restarted is True
    assert result.restart is not None



def test_watchdog_tick_restarts_stale_runtime(tmp_path: Path):
    fake_popen = FakePopen()

    store = RuntimeDaemonStateStore(
        project_root=tmp_path,
        pid_exists_fn=lambda pid: False,
    )

    store.mark_running(
        pid=1234,
        force=True,
    )

    result = run_watchdog_tick(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    assert result.runtime_state == 'stale'
    assert result.restarted is True



def test_watchdog_loop_runs_multiple_iterations(tmp_path: Path):
    fake_popen = FakePopen()

    result = run_watchdog_loop(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
        max_iterations=3,
        sleep_fn=lambda seconds: None,
    )

    assert result.iterations == 3
    assert result.last_tick is not None
    assert result.last_tick.runtime_state in {
        'running',
        'stale',
        'stopped',
    }



def test_watchdog_loop_respects_stop_condition(tmp_path: Path):
    fake_popen = FakePopen()

    result = run_watchdog_loop(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
        sleep_fn=lambda seconds: None,
        should_stop=lambda: True,
    )

    assert result.iterations == 0
