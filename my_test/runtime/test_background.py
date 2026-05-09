from pathlib import Path

import pytest

from runtime.background import launch_background_daemon
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
