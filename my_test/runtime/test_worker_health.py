from pathlib import Path

from runtime.worker_health import (
    RuntimeWorkerHealthStore,
    WORKER_HEALTH_FAILED,
    WORKER_HEALTH_HEALTHY,
)



def test_worker_health_store_marks_success(tmp_path: Path):
    store = RuntimeWorkerHealthStore(project_root=tmp_path)

    result = store.mark_success('worker-a')

    assert result.status == WORKER_HEALTH_HEALTHY
    assert result.success_count == 1



def test_worker_health_store_marks_failure(tmp_path: Path):
    store = RuntimeWorkerHealthStore(project_root=tmp_path)

    result = store.mark_failure(
        'worker-a',
        'boom',
    )

    assert result.status == WORKER_HEALTH_FAILED
    assert result.failure_count == 1
    assert result.last_error == 'boom'



def test_worker_health_store_persists_multiple_workers(tmp_path: Path):
    store = RuntimeWorkerHealthStore(project_root=tmp_path)

    store.mark_success('worker-a')
    store.mark_failure('worker-b', 'failure')

    result = store.read_all()

    assert 'worker-a' in result
    assert 'worker-b' in result
