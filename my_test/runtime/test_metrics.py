from pathlib import Path

from runtime.backoff import RestartBackoffStore
from runtime.metrics import collect_runtime_metrics
from runtime.worker_health import RuntimeWorkerHealthStore
from runtime.worker_quarantine import RuntimeWorkerQuarantineStore



def test_collect_runtime_metrics_aggregates_runtime_state(
    tmp_path: Path,
):
    metrics = collect_runtime_metrics(
        project_root=tmp_path,
    )

    assert metrics.runtime_state in {
        'stopped',
        'running',
        'stale',
    }



def test_collect_runtime_metrics_exposes_lifecycle_state(
    tmp_path: Path,
):
    metrics = collect_runtime_metrics(
        project_root=tmp_path,
    )

    assert metrics.lifecycle_state in {
        'stopped',
        'running',
        'degraded',
        'failed',
    }



def test_collect_runtime_metrics_counts_worker_health(
    tmp_path: Path,
):
    health = RuntimeWorkerHealthStore(
        project_root=tmp_path,
    )

    health.mark_success('worker-a')
    health.mark_failure('worker-b', 'boom')

    metrics = collect_runtime_metrics(
        project_root=tmp_path,
    )

    assert metrics.worker_count == 2
    assert metrics.healthy_workers == 1
    assert metrics.failed_workers == 1



def test_collect_runtime_metrics_counts_quarantined_workers(
    tmp_path: Path,
):
    quarantine = RuntimeWorkerQuarantineStore(
        project_root=tmp_path,
    )

    quarantine.quarantine(
        'worker-a',
        'failure threshold exceeded',
    )

    metrics = collect_runtime_metrics(
        project_root=tmp_path,
    )

    assert metrics.quarantined_workers == 1



def test_collect_runtime_metrics_reports_restart_budget(
    tmp_path: Path,
):
    backoff = RestartBackoffStore(
        project_root=tmp_path,
    )

    backoff.record_restart()

    metrics = collect_runtime_metrics(
        project_root=tmp_path,
    )

    assert metrics.restart_count == 1
