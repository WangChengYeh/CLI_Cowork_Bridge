from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from room.models import RoomEvent
from runtime.worker_health import RuntimeWorkerHealthStore
from runtime.worker_quarantine import (
    RuntimeWorkerQuarantinePolicy,
    RuntimeWorkerQuarantineStore,
    evaluate_worker_quarantine,
)


@dataclass
class RuntimeWorker:
    name: str
    handler: Callable[[RoomEvent], None]
    enabled: bool = True


@dataclass
class RuntimeWorkerRegistry:
    workers: dict[str, RuntimeWorker] = field(default_factory=dict)
    project_root: Optional[Path] = None
    quarantine_policy: RuntimeWorkerQuarantinePolicy = field(
        default_factory=RuntimeWorkerQuarantinePolicy,
    )

    def register(self, worker: RuntimeWorker) -> None:
        self.workers[worker.name] = worker

    def dispatch(self, event: RoomEvent) -> None:
        health_store = None
        quarantine_store = None

        if self.project_root is not None:
            health_store = RuntimeWorkerHealthStore(
                project_root=self.project_root,
            )

            quarantine_store = RuntimeWorkerQuarantineStore(
                project_root=self.project_root,
            )

        for worker in self.workers.values():
            if not worker.enabled:
                continue

            if (
                quarantine_store is not None
                and quarantine_store.is_quarantined(worker.name)
            ):
                continue

            try:
                worker.handler(event)

                if health_store is not None:
                    health = health_store.mark_success(worker.name)

                    if quarantine_store is not None:
                        quarantine_store.recover(worker.name)

            except Exception as error:
                if health_store is not None:
                    health = health_store.mark_failure(
                        worker.name,
                        str(error),
                    )

                    if quarantine_store is not None:
                        quarantine = evaluate_worker_quarantine(
                            worker_health=health,
                            policy=self.quarantine_policy,
                        )

                        if quarantine.quarantined:
                            quarantine_store.quarantine(
                                worker.name,
                                quarantine.reason or 'worker quarantined',
                            )

                continue
