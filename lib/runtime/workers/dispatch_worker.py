from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from room.dispatcher import RoomDispatcher
from room.models import RoomEvent, RoomEventType
from room.store import RoomEventStore
from room.stream_executor import RoomAskStreamExecutor


@dataclass(slots=True)
class DispatchWorkerResult:
    submitted_event_id: str | None
    streamed_event_count: int


class DispatchWorker:
    def __init__(
        self,
        *,
        project_root: Path,
        store: RoomEventStore,
        stream_executor_factory: Callable[..., RoomAskStreamExecutor] | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.store = store
        self.dispatcher = RoomDispatcher(
            project_root=self.project_root,
            store=self.store,
        )
        self.stream_executor_factory = (
            stream_executor_factory or self._default_stream_executor_factory
        )

    def handle(self, event: RoomEvent) -> DispatchWorkerResult:
        if event.type is not RoomEventType.USER_MESSAGE:
            return DispatchWorkerResult(
                submitted_event_id=None,
                streamed_event_count=0,
            )

        dispatch_result = self.dispatcher.dispatch_prepare_only(event)

        executor = self.stream_executor_factory(
            project_root=self.project_root,
            store=self.store,
        )

        stream_result = executor.execute(dispatch_result.request)

        return DispatchWorkerResult(
            submitted_event_id=dispatch_result.submitted_event.event_id,
            streamed_event_count=len(stream_result.output_events),
        )

    @staticmethod
    def _default_stream_executor_factory(**kwargs) -> RoomAskStreamExecutor:
        return RoomAskStreamExecutor(**kwargs)
