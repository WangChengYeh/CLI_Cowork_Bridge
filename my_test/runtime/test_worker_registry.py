from pathlib import Path

from room.models import RoomEvent
from runtime.worker import RuntimeWorker, RuntimeWorkerRegistry
from runtime.worker_health import (
    RuntimeWorkerHealthStore,
    WORKER_HEALTH_FAILED,
    WORKER_HEALTH_HEALTHY,
)



def make_event() -> RoomEvent:
    return RoomEvent(
        room_id='room-1',
        event_type='message',
        payload={},
    )



def test_worker_registry_records_success(tmp_path: Path):
    registry = RuntimeWorkerRegistry(
        project_root=tmp_path,
    )

    registry.register(
        RuntimeWorker(
            name='worker-a',
            handler=lambda event: None,
        )
    )

    registry.dispatch(make_event())

    health = RuntimeWorkerHealthStore(
        project_root=tmp_path,
    ).read_all()['worker-a']

    assert health.status == WORKER_HEALTH_HEALTHY
    assert health.success_count == 1



def test_worker_registry_records_failure(tmp_path: Path):
    registry = RuntimeWorkerRegistry(
        project_root=tmp_path,
    )

    def boom(event):
        raise RuntimeError('failure')

    registry.register(
        RuntimeWorker(
            name='worker-a',
            handler=boom,
        )
    )

    registry.dispatch(make_event())

    health = RuntimeWorkerHealthStore(
        project_root=tmp_path,
    ).read_all()['worker-a']

    assert health.status == WORKER_HEALTH_FAILED
    assert health.failure_count == 1
