from datetime import datetime, timedelta, timezone
from pathlib import Path

from room.models import RoomEvent
from runtime.worker import RuntimeWorker, RuntimeWorkerRegistry
from runtime.worker_quarantine import (
    RuntimeWorkerQuarantinePolicy,
    RuntimeWorkerQuarantineStore,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)



def make_event() -> RoomEvent:
    return RoomEvent(
        room_id='room-1',
        event_type='message',
        payload={},
    )



def test_worker_quarantine_blocks_repeated_failures(tmp_path: Path):
    calls = []

    def boom(event):
        calls.append('called')
        raise RuntimeError('boom')

    registry = RuntimeWorkerRegistry(
        project_root=tmp_path,
    )

    registry.register(
        RuntimeWorker(
            name='worker-a',
            handler=boom,
        )
    )

    registry.dispatch(make_event())
    registry.dispatch(make_event())
    registry.dispatch(make_event())
    registry.dispatch(make_event())

    quarantine = RuntimeWorkerQuarantineStore(
        project_root=tmp_path,
    )

    assert quarantine.is_quarantined('worker-a') is True
    assert len(calls) == 3



def test_worker_quarantine_recovery_clears_quarantine(tmp_path: Path):
    quarantine = RuntimeWorkerQuarantineStore(
        project_root=tmp_path,
    )

    quarantine.quarantine(
        'worker-a',
        'failure threshold exceeded',
    )

    assert quarantine.is_quarantined('worker-a') is True

    quarantine.recover('worker-a')

    assert quarantine.is_quarantined('worker-a') is False



def test_worker_quarantine_cooldown_recovers_worker(tmp_path: Path):
    quarantine = RuntimeWorkerQuarantineStore(
        project_root=tmp_path,
    )

    record = quarantine.quarantine(
        'worker-a',
        'failure threshold exceeded',
    )

    records = quarantine.read_all()
    records['worker-a'].quarantined_at = (
        NOW - timedelta(seconds=600)
    ).isoformat()
    quarantine.write_all(records)

    result = quarantine.is_quarantined(
        'worker-a',
        policy=RuntimeWorkerQuarantinePolicy(
            cooldown_seconds=300,
        ),
        now=NOW,
    )

    assert result is False
