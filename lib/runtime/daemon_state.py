from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'


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


class RuntimeDaemonStateStore:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.state_path = self.project_root / '.ccb' / 'runtime-daemon.json'
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

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
