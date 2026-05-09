from pathlib import Path

import pytest

from runtime.background import (
    launch_background_daemon,
    stop_background_daemon,
)
from runtime.daemon_state import RuntimeDaemonAlreadyRunning


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

        return FakeProcess(pid=4321)



def test_launch_background_daemon_starts_process(tmp_path: Path):
    fake_popen = FakePopen()

    result = launch_background_daemon(
        project_root=tmp_path,
        argv=['ccb', 'daemon', 'start', '--foreground'],
        popen_fn=fake_popen,
    )

    assert result.pid == 4321
    assert result.log_path.exists()
    assert fake_popen.calls



def test_launch_background_daemon_rejects_duplicate_runtime(tmp_path: Path):
    fake_popen = FakePopen()

    launch_background_daemon(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    with pytest.raises(RuntimeDaemonAlreadyRunning):
        launch_background_daemon(
            project_root=tmp_path,
            argv=['ccb'],
            popen_fn=fake_popen,
        )



def test_stop_background_daemon_sends_signal(tmp_path: Path):
    fake_popen = FakePopen()
    kill_calls = []

    launch_background_daemon(
        project_root=tmp_path,
        argv=['ccb'],
        popen_fn=fake_popen,
    )

    result = stop_background_daemon(
        project_root=tmp_path,
        kill_fn=lambda pid, signum: kill_calls.append(
            (pid, signum)
        ),
    )

    assert result.signaled is True
    assert result.pid == 4321
    assert kill_calls



def test_stop_background_daemon_handles_stopped_runtime(tmp_path: Path):
    result = stop_background_daemon(
        project_root=tmp_path,
        kill_fn=lambda pid, signum: None,
    )

    assert result.signaled is False
    assert result.reason is not None
