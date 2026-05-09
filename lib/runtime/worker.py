from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from room.models import RoomEvent


@dataclass(slots=True)
class RuntimeWorker:
    name: str
    handler: Callable[[RoomEvent], None]
    enabled: bool = True


@dataclass(slots=True)
class RuntimeWorkerRegistry:
    workers: dict[str, RuntimeWorker] = field(default_factory=dict)

    def register(self, worker: RuntimeWorker) -> None:
        self.workers[worker.name] = worker

    def dispatch(self, event: RoomEvent) -> None:
        for worker in self.workers.values():
            if not worker.enabled:
                continue
            worker.handler(event)
