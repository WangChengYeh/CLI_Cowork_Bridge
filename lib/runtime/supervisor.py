from __future__ import annotations

from typing import Optional

from dataclasses import dataclass
from pathlib import Path

from room.models import RoomEvent
from room.store import RoomEventStore

from .event_loop import RuntimeEventLoop, RuntimeLoopResult
from .worker import RuntimeWorker, RuntimeWorkerRegistry


@dataclass
class SupervisorStatus:
    worker_count: int
    cursor_name: str


class RuntimeSupervisor:
    def __init__(
        self,
        *,
        project_root: Path,
        store: Optional[RoomEventStore] = None,
        event_loop: Optional[RuntimeEventLoop] = None,
    ) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.registry = RuntimeWorkerRegistry()
        self.loop = event_loop or RuntimeEventLoop(
            project_root=project_root,
            store=self.store,
            on_event=self.registry.dispatch,
        )

        if self.loop.on_event is None:
            self.loop.on_event = self.registry.dispatch

    def register_worker(self, worker: RuntimeWorker) -> None:
        self.registry.register(worker)

    def poll_once(self) -> RuntimeLoopResult:
        return self.loop.poll_once()

    def run_forever(self) -> None:
        self.loop.run_forever()

    def status(self) -> SupervisorStatus:
        return SupervisorStatus(
            worker_count=len(self.registry.workers),
            cursor_name=self.loop.cursor_name,
        )
