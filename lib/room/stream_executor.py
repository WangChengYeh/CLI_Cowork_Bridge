from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from .dispatcher import RoomDispatchRequest
from .models import RoomEvent, RoomEventType, RoomSource
from .store import RoomEventStore


class RoomStreamExecutionError(RuntimeError):
    pass


@dataclass(slots=True)
class RoomStreamExecutionResult:
    request: RoomDispatchRequest
    returncode: int
    output_events: list[RoomEvent] = field(default_factory=list)
    terminal_event: RoomEvent | None = None


class RoomAskStreamExecutor:
    def __init__(
        self,
        *,
        project_root: Path,
        store: RoomEventStore | None = None,
        ccb_path: Path | None = None,
        popen_fn: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    ) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.ccb_path = ccb_path or self._default_ccb_path()
        self.popen_fn = popen_fn

    def execute(self, request: RoomDispatchRequest) -> RoomStreamExecutionResult:
        if request.is_broadcast:
            raise RoomStreamExecutionError('broadcast execution is not supported by stream executor')

        argv = [str(self.ccb_path), *request.to_ask_argv()]
        process = self.popen_fn(
            argv,
            cwd=str(self.project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        output_events: list[RoomEvent] = []

        if process.stdout is not None:
            for line in process.stdout:
                body = line.rstrip('\n')
                if not body.strip():
                    continue
                event = self._append_agent_message(request, body=body)
                output_events.append(event)

        returncode = process.wait()
        terminal_event = self._append_terminal_event(
            request,
            returncode=returncode,
            output_count=len(output_events),
        )

        return RoomStreamExecutionResult(
            request=request,
            returncode=returncode,
            output_events=output_events,
            terminal_event=terminal_event,
        )

    def _append_agent_message(self, request: RoomDispatchRequest, *, body: str) -> RoomEvent:
        event = RoomEvent(
            room_id=request.room_id,
            source=RoomSource.AGENT,
            sender=request.target,
            target=request.sender,
            type=RoomEventType.AGENT_MESSAGE,
            body=body,
            parent_event_id=request.source_event_id,
            correlation_id=request.source_event_id,
            metadata={
                'source': request.source,
                'stream': True,
            },
        )
        self.store.append(event)
        return event

    def _append_terminal_event(
        self,
        request: RoomDispatchRequest,
        *,
        returncode: int,
        output_count: int,
    ) -> RoomEvent:
        event_type = RoomEventType.TASK_COMPLETED if returncode == 0 else RoomEventType.TASK_FAILED
        event = RoomEvent(
            room_id=request.room_id,
            source=RoomSource.SYSTEM,
            sender='room-stream-executor',
            target=request.target,
            type=event_type,
            body=f'ccb ask exited with {returncode}',
            parent_event_id=request.source_event_id,
            correlation_id=request.source_event_id,
            metadata={
                'returncode': returncode,
                'output_count': output_count,
                'stream': True,
            },
        )
        self.store.append(event)
        return event

    def _default_ccb_path(self) -> Path:
        candidate = self.project_root / 'ccb'
        if candidate.exists():
            return candidate
        return Path(__file__).resolve().parents[2] / 'ccb'
