from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from runtime.backoff import (
    RestartBackoffPolicy,
    RestartBackoffStore,
    evaluate_restart_backoff,
)
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
    runtime_state: str
    health: RuntimeHealth
    restarted: bool
    restart: BackgroundDaemonRestartResult | None = None
    backoff_reason: str | None = None


@dataclass(slots=True)
class RuntimeWatchdogLoopResult:
    iterations: int
    restarts: int
    last_tick: RuntimeWatchdogTickResult | None = None


def run_watchdog_tick(
    *,
    project_root: Path,
    argv: Sequence[str] | None = None,
    popen_fn: Callable[..., subprocess.Popen] = subprocess.Popen,
    heartbeat_timeout_seconds: int = 60,
    restart_policy: RestartBackoffPolicy | None = None,
) -> RuntimeWatchdogTickResult:
    state_store = RuntimeDaemonStateStore(project_root=project_root)
    state = state_store.read_resolved()
    health = evaluate_runtime_health(
        state,
        heartbeat_timeout_seconds=heartbeat_timeout_seconds,
    )

    if health.status == HEALTH_HEALTHY:
        RestartBackoffStore(project_root=project_root).reset()

        return RuntimeWatchdogTickResult(
            runtime_state=state.state,
            health=health,
            restarted=False,
            restart=None,
            backoff_reason=None,
        )

    backoff_store = RestartBackoffStore(project_root=project_root)
    decision = evaluate_restart_backoff(
        store=backoff_store,
        policy=restart_policy,
    )

    if not decision.allowed:
        return RuntimeWatchdogTickResult(
            runtime_state=state.state,
            health=health,
            restarted=False,
            restart=None,
            backoff_reason=decision.reason,
        )

    restart = restart_background_daemon_if_needed(
        project_root=project_root,
        argv=argv,
        popen_fn=popen_fn,
    )

    if restart.restarted:
        backoff_store.record_restart()

    return RuntimeWatchdogTickResult(
        runtime_state=state.state,
        health=health,
        restarted=restart.restarted,
        restart=restart,
        backoff_reason=decision.reason,
    )


def run_watchdog_loop(
    *,
    project_root: Path,
    argv: Sequence[str] | None = None,
    popen_fn: Callable[..., subprocess.Popen] = subprocess.Popen,
    heartbeat_timeout_seconds: int = 60,
    interval_seconds: float = 5.0,
    max_iterations: int | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    should_stop: Callable[[], bool] | None = None,
    restart_policy: RestartBackoffPolicy | None = None,
) -> RuntimeWatchdogLoopResult:
    iterations = 0
    restarts = 0
    last_tick: RuntimeWatchdogTickResult | None = None

    while True:
        if should_stop is not None and should_stop():
            break

        last_tick = run_watchdog_tick(
            project_root=project_root,
            argv=argv,
            popen_fn=popen_fn,
            heartbeat_timeout_seconds=heartbeat_timeout_seconds,
            restart_policy=restart_policy,
        )

        iterations += 1

        if last_tick.restarted:
            restarts += 1

        if max_iterations is not None and iterations >= max_iterations:
            break

        sleep_fn(interval_seconds)

    return RuntimeWatchdogLoopResult(
        iterations=iterations,
        restarts=restarts,
        last_tick=last_tick,
    )
