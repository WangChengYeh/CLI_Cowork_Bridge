from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'
STATE_STALE = 'stale'


@dataclass(slots=True)
class RuntimeDaemonState:
    state: str
    pid: int | None
    updated_at: str
    heartbeat_at: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            'state': self.state,
            'pid': self.pid,
            'updated_at': self.updated_at,
            'heartbeat_at': self.heartbeat_at,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> 'RuntimeDaemonState':
        return cls(
            state=str(record.get('state') or STATE_STOPPED),
            pid=record.get('pid'),
            updated_at=str(record.get('updated_at') or now_utc()),
            heartbeat_at=record.get('heartbeat_at'),
        )


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def pid_exists(pid: int | None) -> bool:
    if pid is None or pid <= 0:
        return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    return True


class RuntimeDaemonStateStore:
    def __init__(
        self,
        *,
        project_root: Path,
        pid_exists_fn: Callable[[int | None], bool] = pid_exists,
    ) -> None:
        self.project_root = Path(project_root)
        self.state_path = self.project_root / '.ccb' / 'runtime-daemon.json'
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.pid_exists_fn = pid_exists_fn

    def read(self) -> RuntimeDaemonState:
        if not self.state_path.exists():
            return RuntimeDaemonState(
                state=STATE_STOPPED,
                pid=None,
                updated_at=now_utc(),
                heartbeat_at=None,
            )

        with self.state_path.open('r', encoding='utf-8') as handle:
            return RuntimeDaemonState.from_record(json.load(handle))

    def read_resolved(self) -> RuntimeDaemonState:
        state = self.read()

        if state.state == STATE_RUNNING and not self.pid_exists_fn(state.pid):
            return RuntimeDaemonState(
                state=STATE_STALE,
                pid=state.pid,
                updated_at=state.updated_at,
                heartbeat_at=state.heartbeat_at,
            )

        return state

    def write(self, state: RuntimeDaemonState) -> RuntimeDaemonState:
        tmp_path = self.state_path.with_suffix('.json.tmp')

        with tmp_path.open('w', encoding='utf-8') as handle:
            json.dump(state.to_record(), handle, indent=2, sort_keys=True)
            handle.write('\n')

        tmp_path.replace(self.state_path)
        return state

    def mark_running(self, *, pid: int | None = None) -> RuntimeDaemonState:
        timestamp = now_utc()
        return self.write(
            RuntimeDaemonState(
                state=STATE_RUNNING,
                pid=pid if pid is not None else os.getpid(),
                updated_at=timestamp,
                heartbeat_at=timestamp,
            )
        )

    def mark_stopped(self) -> RuntimeDaemonState:
        return self.write(
            RuntimeDaemonState(
                state=STATE_STOPPED,
                pid=None,
                updated_at=now_utc(),
                heartbeat_at=None,
            )
        )

    def heartbeat(self) -> RuntimeDaemonState:
        current = self.read()
        current.heartbeat_at = now_utc()
        current.updated_at = current.heartbeat_at
        return self.write(current)
