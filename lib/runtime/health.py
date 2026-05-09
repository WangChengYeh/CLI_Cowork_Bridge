from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from runtime.daemon_state import (
    STATE_RUNNING,
    STATE_STALE,
    STATE_STOPPED,
    RuntimeDaemonState,
)


HEALTH_HEALTHY = 'healthy'
HEALTH_STALE = 'stale'
HEALTH_STOPPED = 'stopped'
HEALTH_UNKNOWN = 'unknown'


@dataclass(slots=True)
class RuntimeHealth:
    status: str
    score: int
    reason: str


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def evaluate_runtime_health(
    state: RuntimeDaemonState,
    *,
    now: datetime | None = None,
    heartbeat_timeout_seconds: int = 60,
) -> RuntimeHealth:
    now = now or datetime.now(timezone.utc)

    if state.state == STATE_STOPPED:
        return RuntimeHealth(
            status=HEALTH_STOPPED,
            score=0,
            reason='daemon is stopped',
        )

    if state.state == STATE_STALE:
        return RuntimeHealth(
            status=HEALTH_STALE,
            score=25,
            reason='daemon pid is stale',
        )

    if state.state != STATE_RUNNING:
        return RuntimeHealth(
            status=HEALTH_UNKNOWN,
            score=10,
            reason=f'unknown daemon state: {state.state}',
        )

    heartbeat = parse_timestamp(state.heartbeat_at)

    if heartbeat is None:
        return RuntimeHealth(
            status=HEALTH_STALE,
            score=40,
            reason='missing heartbeat',
        )

    age = (now - heartbeat).total_seconds()

    if age > heartbeat_timeout_seconds:
        return RuntimeHealth(
            status=HEALTH_STALE,
            score=50,
            reason=f'heartbeat timeout: {int(age)}s',
        )

    return RuntimeHealth(
        status=HEALTH_HEALTHY,
        score=100,
        reason='daemon heartbeat is fresh',
    )
