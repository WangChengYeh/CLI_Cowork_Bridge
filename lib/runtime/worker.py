from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from room.models import RoomEvent
from runtime.worker_health import RuntimeWorkerHealthStore


@dataclass(slots=True)
class RuntimeWorker:
    name: str
    handler: Callable[[RoomEvent], None]
    enabled: bool = True


@dataclass(slots=True)
class RuntimeWorkerRegistry:
    workers: dict[str, RuntimeWorker] = field(default_factory=dict)
    project_root: Path | None = None

    def register(self, worker: RuntimeWorker) -> None:
        self.workers[worker.name] = worker

    def dispatch(self, event: RoomEvent) -> None:
        health_store = None

        if self.project_root is not None:
            health_store = RuntimeWorkerHealthStore(
                project_root=self.project_root,
            )

        for worker in self.workers.values():
            if not worker.enabled:
                continue

            try:
                worker.handler(event)

                if health_store is not None:
                    health_store.mark_success(worker.name)

            except Exception as error:
                if health_store is not None:
                    health_store.mark_failure(
                        worker.name,
                        str(error),
                    )

                continue
