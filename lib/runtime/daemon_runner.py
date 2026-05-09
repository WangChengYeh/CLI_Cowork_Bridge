from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from runtime.bootstrap import RuntimeBootstrap, bootstrap_runtime
from runtime.daemon_state import RuntimeDaemonStateStore


@dataclass(slots=True)
class RuntimeDaemonRunResult:
    iterations: int
    processed_events: int


def run_runtime_forever(
    *,
    project_root: Path,
    interval_seconds: float = 1.0,
    max_iterations: int | None = None,
    bootstrap: RuntimeBootstrap | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> RuntimeDaemonRunResult:
    runtime = bootstrap or bootstrap_runtime(project_root=project_root)
    state_store = RuntimeDaemonStateStore(project_root=project_root)

    state_store.mark_running()

    iterations = 0
    processed_events = 0

    while True:
        state_store.heartbeat()
        result = runtime.supervisor.poll_once()
        processed_events += result.processed_events
        iterations += 1
        state_store.heartbeat()

        if max_iterations is not None and iterations >= max_iterations:
            break

        sleep_fn(interval_seconds)

    return RuntimeDaemonRunResult(
        iterations=iterations,
        processed_events=processed_events,
    )
