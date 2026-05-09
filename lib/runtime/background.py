from __future__ import annotations

import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Sequence

from runtime.daemon_state import (
    STATE_RUNNING,
    STATE_STALE,
    RuntimeDaemonStateStore,
)


@dataclass
class BackgroundDaemonLaunchResult:
    pid: int
    argv: list[str]
    log_path: Path


@dataclass
class BackgroundDaemonStopResult:
    signaled: bool
    pid: Optional[int]
    reason: Optional[str] = None


@dataclass
class BackgroundDaemonRestartResult:
    restarted: bool
    launch: Optional[BackgroundDaemonLaunchResult]
    reason: Optional[str] = None


def default_daemon_argv(project_root: Path) -> list[str]:
    ccb_path = project_root / 'ccb'

    if ccb_path.exists():
        return [str(ccb_path), 'daemon', 'start', '--foreground']

    return [
        sys.executable,
        '-m',
        'cli.daemon_cli',
        'start',
        '--foreground',
    ]


def launch_background_daemon(
    *,
    project_root: Path,
    argv: Optional[Sequence[str]] = None,
    popen_fn: Callable[..., subprocess.Popen] = subprocess.Popen,
) -> BackgroundDaemonLaunchResult:
    project_root = Path(project_root)

    state_store = RuntimeDaemonStateStore(project_root=project_root)
    state_store.ensure_can_start()

    log_path = project_root / '.ccb' / 'runtime-daemon.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)

    launch_argv = list(argv) if argv is not None else default_daemon_argv(project_root)

    with log_path.open('ab') as log_handle:
        process = popen_fn(
            launch_argv,
            cwd=str(project_root),
            stdout=log_handle,
            stderr=log_handle,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    state_store.mark_running(pid=process.pid, force=True)

    return BackgroundDaemonLaunchResult(
        pid=process.pid,
        argv=launch_argv,
        log_path=log_path,
    )


def stop_background_daemon(
    *,
    project_root: Path,
    signum: int = signal.SIGTERM,
    kill_fn: Callable[[int, int], None] = os.kill,
) -> BackgroundDaemonStopResult:
    state_store = RuntimeDaemonStateStore(project_root=project_root)
    state = state_store.read_resolved()

    if state.state != STATE_RUNNING:
        state_store.mark_stopped()
        return BackgroundDaemonStopResult(
            signaled=False,
            pid=state.pid,
            reason=f'daemon is not running: {state.state}',
        )

    if state.pid is None:
        state_store.mark_stopped()
        return BackgroundDaemonStopResult(
            signaled=False,
            pid=None,
            reason='daemon pid is missing',
        )

    kill_fn(state.pid, signum)
    state_store.mark_stopped()

    return BackgroundDaemonStopResult(
        signaled=True,
        pid=state.pid,
        reason=None,
    )


def restart_background_daemon_if_needed(
    *,
    project_root: Path,
    argv: Optional[Sequence[str]] = None,
    popen_fn: Callable[..., subprocess.Popen] = subprocess.Popen,
) -> BackgroundDaemonRestartResult:
    state_store = RuntimeDaemonStateStore(project_root=project_root)
    state = state_store.read_resolved()

    if state.state == STATE_RUNNING:
        return BackgroundDaemonRestartResult(
            restarted=False,
            launch=None,
            reason=f'daemon already running with pid={state.pid}',
        )

    if state.state == STATE_STALE:
        state_store.mark_stopped()

    launch = launch_background_daemon(
        project_root=project_root,
        argv=argv,
        popen_fn=popen_fn,
    )

    return BackgroundDaemonRestartResult(
        restarted=True,
        launch=launch,
        reason=None,
    )
