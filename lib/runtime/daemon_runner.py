from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from runtime.bootstrap import RuntimeBootstrap, bootstrap_runtime
from runtime.daemon_state import RuntimeDaemonStateStore


@dataclass
class RuntimeDaemonRunResult:
    iterations: int
    processed_events: int
    stopped_by_condition: bool = False


def run_runtime_forever(
    *,
    project_root: Path,
    interval_seconds: float = 1.0,
    max_iterations: Optional[int] = None,
    bootstrap: Optional[RuntimeBootstrap] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    should_stop: Callable[[], Optional[bool]] = None,
) -> RuntimeDaemonRunResult:
    runtime = bootstrap or bootstrap_runtime(project_root=project_root)
    state_store = RuntimeDaemonStateStore(project_root=project_root)

    state_store.mark_running(force=True)

    iterations = 0
    processed_events = 0
    stopped_by_condition = False

    last_imessage_poll = 0.0
    imessage_poll_interval = 10.0

    while True:
        if should_stop is not None and should_stop():
            stopped_by_condition = True
            break

        now = time.time()
        if now - last_imessage_poll >= imessage_poll_interval:
            runtime.watcher.poll_once()
            last_imessage_poll = now

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
        stopped_by_condition=stopped_by_condition,
    )
