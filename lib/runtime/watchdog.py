from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from runtime.background import (
    BackgroundDaemonRestartResult,
    restart_background_daemon_if_needed,
)
from runtime.daemon_state import RuntimeDaemonStateStore
from runtime.health import (
    HEALTH_HEALTHY,
    RuntimeHealth,
    evaluate_runtime_health,
)


@dataclass(slots=True)
class RuntimeWatchdogTickResult:
    health: RuntimeHealth
    restarted: bool
    restart: BackgroundDaemonRestartResult | None = None


def run_watchdog_tick(
    *,
    project_root: Path,
    argv: Sequence[str] | None = None,
    popen_fn: Callable[..., subprocess.Popen] = subprocess.Popen,
    heartbeat_timeout_seconds: int = 60,
) -> RuntimeWatchdogTickResult:
    state_store = RuntimeDaemonStateStore(project_root=project_root)
    state = state_store.read_resolved()
    health = evaluate_runtime_health(
        state,
        heartbeat_timeout_seconds=heartbeat_timeout_seconds,
    )

    if health.status == HEALTH_HEALTHY:
        return RuntimeWatchdogTickResult(
            health=health,
            restarted=False,
            restart=None,
        )

    restart = restart_background_daemon_if_needed(
        project_root=project_root,
        argv=argv,
        popen_fn=popen_fn,
    )

    return RuntimeWatchdogTickResult(
        health=health,
        restarted=restart.restarted,
        restart=restart,
    )
