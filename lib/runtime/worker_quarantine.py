from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.worker_health import RuntimeWorkerHealth


@dataclass(slots=True)
class RuntimeWorkerQuarantinePolicy:
    failure_threshold: int = 3
    cooldown_seconds: int = 300


@dataclass(slots=True)
class RuntimeWorkerQuarantineRecord:
    worker_name: str
    quarantined: bool
    reason: str | None = None
    quarantined_at: str | None = None


class RuntimeWorkerQuarantineStore:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.path = self.project_root / '.ccb' / 'worker-quarantine.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_all(self) -> dict[str, RuntimeWorkerQuarantineRecord]:
        if not self.path.exists():
            return {}

        with self.path.open('r', encoding='utf-8') as handle:
            raw = json.load(handle)

        return {
            name: RuntimeWorkerQuarantineRecord(
                worker_name=name,
                quarantined=bool(record.get('quarantined')),
                reason=record.get('reason'),
                quarantined_at=record.get('quarantined_at'),
            )
            for name, record in raw.items()
        }

    def write_all(
        self,
        records: dict[str, RuntimeWorkerQuarantineRecord],
    ) -> None:
        payload: dict[str, Any] = {
            name: {
                'quarantined': record.quarantined,
                'reason': record.reason,
                'quarantined_at': record.quarantined_at,
            }
            for name, record in records.items()
        }

        tmp_path = self.path.with_suffix('.json.tmp')

        with tmp_path.open('w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write('\n')

        tmp_path.replace(self.path)

    def quarantine(
        self,
        worker_name: str,
        reason: str,
    ) -> RuntimeWorkerQuarantineRecord:
        records = self.read_all()

        record = RuntimeWorkerQuarantineRecord(
            worker_name=worker_name,
            quarantined=True,
            reason=reason,
            quarantined_at=datetime.now(timezone.utc).isoformat(),
        )

        records[worker_name] = record
        self.write_all(records)
        return record

    def recover(self, worker_name: str) -> None:
        records = self.read_all()

        if worker_name in records:
            del records[worker_name]

        self.write_all(records)

    def is_quarantined(
        self,
        worker_name: str,
        *,
        policy: RuntimeWorkerQuarantinePolicy | None = None,
        now: datetime | None = None,
    ) -> bool:
        records = self.read_all()
        record = records.get(worker_name)

        if not record or not record.quarantined:
            return False

        policy = policy or RuntimeWorkerQuarantinePolicy()
        now = now or datetime.now(timezone.utc)

        if record.quarantined_at:
            try:
                quarantined_at = datetime.fromisoformat(
                    record.quarantined_at,
                )

                age = (now - quarantined_at).total_seconds()

                if age > policy.cooldown_seconds:
                    self.recover(worker_name)
                    return False

            except ValueError:
                pass

        return True


def evaluate_worker_quarantine(
    *,
    worker_health: RuntimeWorkerHealth,
    policy: RuntimeWorkerQuarantinePolicy | None = None,
) -> RuntimeWorkerQuarantineRecord:
    policy = policy or RuntimeWorkerQuarantinePolicy()

    quarantined = (
        worker_health.failure_count >= policy.failure_threshold
    )

    return RuntimeWorkerQuarantineRecord(
        worker_name=worker_health.worker_name,
        quarantined=quarantined,
        reason=(
            f'failure threshold exceeded: '
            f'{worker_health.failure_count}/'
            f'{policy.failure_threshold}'
            if quarantined
            else None
        ),
    )
