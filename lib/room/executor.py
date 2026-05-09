from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .dispatcher import RoomDispatchRequest
from .models import RoomEvent, RoomEventType, RoomSource
from .store import RoomEventStore


class RoomExecutionError(RuntimeError):
    pass


@dataclass(slots=True)
class RoomExecutionResult:
    request: RoomDispatchRequest
    returncode: int
    stdout: str
    stderr: str
    event: RoomEvent


class RoomAskExecutor:
    def __init__(
        self,
        *,
        project_root: Path,
        store: RoomEventStore | None = None,
        ccb_path: Path | None = None,
        run_fn: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.project_root = project_root
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')
        self.ccb_path = ccb_path or self._default_ccb_path()
        self.run_fn = run_fn

    def execute(self, request: RoomDispatchRequest) -> RoomExecutionResult:
        argv = [str(self.ccb_path), *request.to_ask_argv()]

        process = self.run_fn(
            argv,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )

        event_type = (
            RoomEventType.TASK_COMPLETED
            if process.returncode == 0
            else RoomEventType.TASK_FAILED
        )

        body = process.stdout.strip() or process.stderr.strip() or f'ccb ask exited with {process.returncode}'

        event = RoomEvent(
            room_id=request.room_id,
            source=RoomSource.SYSTEM,
            sender='room-executor',
            target=request.target,
            type=event_type,
            body=body,
            parent_event_id=request.source_event_id,
            correlation_id=request.source_event_id,
            metadata={
                'argv': argv,
                'returncode': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr,
            },
        )
        self.store.append(event)

        return RoomExecutionResult(
            request=request,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
            event=event,
        )

    def _default_ccb_path(self) -> Path:
        candidate = self.project_root / 'ccb'
        if candidate.exists():
            return candidate
        return Path(__file__).resolve().parents[2] / 'ccb'
