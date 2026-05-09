from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class RestartBackoffDecision:
    allowed: bool
    reason: str
    restart_count: int


@dataclass
class RestartBackoffPolicy:
    max_restarts: int = 3
    window_seconds: int = 300


class RestartBackoffStore:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.path = self.project_root / '.ccb' / 'runtime-backoff.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                'restart_count': 0,
                'last_restart_at': None,
            }

        with self.path.open('r', encoding='utf-8') as handle:
            return json.load(handle)

    def write(self, record: dict[str, Any]) -> dict[str, Any]:
        tmp_path = self.path.with_suffix('.json.tmp')

        with tmp_path.open('w', encoding='utf-8') as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write('\n')

        tmp_path.replace(self.path)
        return record

    def reset(self) -> dict[str, Any]:
        return self.write(
            {
                'restart_count': 0,
                'last_restart_at': None,
            }
        )

    def record_restart(self, *, now: Optional[datetime] = None) -> dict[str, Any]:
        record = self.read()
        count = int(record.get('restart_count') or 0) + 1
        now = now or datetime.now(timezone.utc)

        return self.write(
            {
                'restart_count': count,
                'last_restart_at': now.isoformat(),
            }
        )


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def evaluate_restart_backoff(
    *,
    store: RestartBackoffStore,
    policy: Optional[RestartBackoffPolicy] = None,
    now: Optional[datetime] = None,
) -> RestartBackoffDecision:
    policy = policy or RestartBackoffPolicy()
    now = now or datetime.now(timezone.utc)
    record = store.read()
    count = int(record.get('restart_count') or 0)
    last_restart = parse_timestamp(record.get('last_restart_at'))

    if last_restart is not None:
        age = (now - last_restart).total_seconds()

        if age > policy.window_seconds:
            store.reset()
            count = 0

    if count >= policy.max_restarts:
        return RestartBackoffDecision(
            allowed=False,
            reason=f'restart limit reached: {count}/{policy.max_restarts}',
            restart_count=count,
        )

    return RestartBackoffDecision(
        allowed=True,
        reason=f'restart allowed: {count}/{policy.max_restarts}',
        restart_count=count,
    )
