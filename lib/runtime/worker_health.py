from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


WORKER_HEALTH_HEALTHY = 'healthy'
WORKER_HEALTH_FAILED = 'failed'
WORKER_HEALTH_UNKNOWN = 'unknown'


@dataclass
class RuntimeWorkerHealth:
    worker_name: str
    status: str
    success_count: int = 0
    failure_count: int = 0
    last_success_at: Optional[str] = None
    last_failure_at: Optional[str] = None
    last_error: Optional[str] = None

    def to_record(self) -> dict[str, Any]:
        return {
            'worker_name': self.worker_name,
            'status': self.status,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_success_at': self.last_success_at,
            'last_failure_at': self.last_failure_at,
            'last_error': self.last_error,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> 'RuntimeWorkerHealth':
        return cls(
            worker_name=str(record.get('worker_name') or ''),
            status=str(record.get('status') or WORKER_HEALTH_UNKNOWN),
            success_count=int(record.get('success_count') or 0),
            failure_count=int(record.get('failure_count') or 0),
            last_success_at=record.get('last_success_at'),
            last_failure_at=record.get('last_failure_at'),
            last_error=record.get('last_error'),
        )


class RuntimeWorkerHealthStore:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.path = self.project_root / '.ccb' / 'worker-health.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_all(self) -> dict[str, RuntimeWorkerHealth]:
        if not self.path.exists():
            return {}

        with self.path.open('r', encoding='utf-8') as handle:
            raw = json.load(handle)

        return {
            name: RuntimeWorkerHealth.from_record(record)
            for name, record in raw.items()
        }

    def write_all(
        self,
        health: dict[str, RuntimeWorkerHealth],
    ) -> dict[str, RuntimeWorkerHealth]:
        tmp_path = self.path.with_suffix('.json.tmp')
        record = {
            name: item.to_record()
            for name, item in health.items()
        }

        with tmp_path.open('w', encoding='utf-8') as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write('\n')

        tmp_path.replace(self.path)
        return health

    def mark_success(self, worker_name: str) -> RuntimeWorkerHealth:
        all_health = self.read_all()
        current = all_health.get(
            worker_name,
            RuntimeWorkerHealth(
                worker_name=worker_name,
                status=WORKER_HEALTH_UNKNOWN,
            ),
        )

        current.status = WORKER_HEALTH_HEALTHY
        current.success_count += 1
        current.last_success_at = datetime.now(timezone.utc).isoformat()
        current.last_error = None

        all_health[worker_name] = current
        self.write_all(all_health)
        return current

    def mark_failure(
        self,
        worker_name: str,
        error: str,
    ) -> RuntimeWorkerHealth:
        all_health = self.read_all()
        current = all_health.get(
            worker_name,
            RuntimeWorkerHealth(
                worker_name=worker_name,
                status=WORKER_HEALTH_UNKNOWN,
            ),
        )

        current.status = WORKER_HEALTH_FAILED
        current.failure_count += 1
        current.last_failure_at = datetime.now(timezone.utc).isoformat()
        current.last_error = error

        all_health[worker_name] = current
        self.write_all(all_health)
        return current
