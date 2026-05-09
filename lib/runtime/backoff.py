from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RestartBackoffDecision:
    allowed: bool
    reason: str
    restart_count: int


@dataclass(slots=True)
class RestartBackoffPolicy:
    max_restarts: int = 3


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

    def record_restart(self) -> dict[str, Any]:
        record = self.read()
        count = int(record.get('restart_count') or 0) + 1

        return self.write(
            {
                'restart_count': count,
                'last_restart_at': datetime.now(timezone.utc).isoformat(),
            }
        )


def evaluate_restart_backoff(
    *,
    store: RestartBackoffStore,
    policy: RestartBackoffPolicy | None = None,
) -> RestartBackoffDecision:
    policy = policy or RestartBackoffPolicy()
    record = store.read()
    count = int(record.get('restart_count') or 0)

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
