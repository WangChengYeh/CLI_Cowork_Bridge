from pathlib import Path

from runtime.daemon_state import (
    STATE_RUNNING,
    STATE_STOPPED,
    RuntimeDaemonStateStore,
)



def test_default_state_is_stopped(tmp_path: Path):
    store = RuntimeDaemonStateStore(
        project_root=tmp_path,
    )

    state = store.read()

    assert state.state == STATE_STOPPED
    assert state.pid is None



def test_mark_running_persists_pid(tmp_path: Path):
    store = RuntimeDaemonStateStore(
        project_root=tmp_path,
    )

    state = store.mark_running(pid=1234)

    assert state.state == STATE_RUNNING
    assert state.pid == 1234

    restored = store.read()

    assert restored.state == STATE_RUNNING
    assert restored.pid == 1234



def test_mark_stopped_clears_pid(tmp_path: Path):
    store = RuntimeDaemonStateStore(
        project_root=tmp_path,
    )

    store.mark_running(pid=1234)

    stopped = store.mark_stopped()

    assert stopped.state == STATE_STOPPED
    assert stopped.pid is None



def test_heartbeat_updates_timestamp(tmp_path: Path):
    store = RuntimeDaemonStateStore(
        project_root=tmp_path,
    )

    store.mark_running(pid=1234)

    first = store.read().heartbeat_at

    updated = store.heartbeat()

    assert updated.heartbeat_at is not None
    assert updated.heartbeat_at >= first
