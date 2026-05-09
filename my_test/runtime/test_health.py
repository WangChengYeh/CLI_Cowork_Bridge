from datetime import datetime, timedelta, timezone

from runtime.daemon_state import (
    STATE_RUNNING,
    STATE_STALE,
    STATE_STOPPED,
    RuntimeDaemonState,
)
from runtime.health import (
    HEALTH_HEALTHY,
    HEALTH_STALE,
    HEALTH_STOPPED,
    evaluate_runtime_health,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)



def test_stopped_runtime_has_zero_health_score():
    health = evaluate_runtime_health(
        RuntimeDaemonState(
            state=STATE_STOPPED,
            pid=None,
            updated_at=NOW.isoformat(),
            heartbeat_at=None,
        ),
        now=NOW,
    )

    assert health.status == HEALTH_STOPPED
    assert health.score == 0



def test_stale_runtime_is_detected():
    health = evaluate_runtime_health(
        RuntimeDaemonState(
            state=STATE_STALE,
            pid=1234,
            updated_at=NOW.isoformat(),
            heartbeat_at=NOW.isoformat(),
        ),
        now=NOW,
    )

    assert health.status == HEALTH_STALE



def test_running_runtime_with_fresh_heartbeat_is_healthy():
    health = evaluate_runtime_health(
        RuntimeDaemonState(
            state=STATE_RUNNING,
            pid=1234,
            updated_at=NOW.isoformat(),
            heartbeat_at=(
                NOW - timedelta(seconds=5)
            ).isoformat(),
        ),
        now=NOW,
    )

    assert health.status == HEALTH_HEALTHY
    assert health.score == 100



def test_running_runtime_with_old_heartbeat_is_stale():
    health = evaluate_runtime_health(
        RuntimeDaemonState(
            state=STATE_RUNNING,
            pid=1234,
            updated_at=NOW.isoformat(),
            heartbeat_at=(
                NOW - timedelta(seconds=300)
            ).isoformat(),
        ),
        now=NOW,
        heartbeat_timeout_seconds=60,
    )

    assert health.status == HEALTH_STALE
    assert health.score < 100
