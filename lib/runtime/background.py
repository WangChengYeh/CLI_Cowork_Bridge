from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from runtime.daemon_state import RuntimeDaemonStateStore


@dataclass(slots=True)
class BackgroundDaemonLaunchResult:
    pid: int
    argv: list[str]
    log_path: Path


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
    argv: Sequence[str] | None = None,
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
