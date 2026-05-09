from pathlib import Path

from room.models import RoomEvent
from runtime.worker import RuntimeWorker, RuntimeWorkerRegistry
from runtime.worker_quarantine import RuntimeWorkerQuarantineStore



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
