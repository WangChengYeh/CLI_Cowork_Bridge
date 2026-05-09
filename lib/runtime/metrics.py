from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from runtime.backoff import RestartBackoffStore
from runtime.daemon_state import RuntimeDaemonStateStore
from runtime.health import evaluate_runtime_health
from runtime.worker_health import RuntimeWorkerHealthStore
from runtime.worker_quarantine import RuntimeWorkerQuarantineStore


@dataclass(slots=True)
class RuntimeMetricsSnapshot:
    runtime_state: str
    runtime_health: str
    runtime_health_score: int
    restart_count: int
    worker_count: int
    quarantined_workers: int
    healthy_workers: int
    failed_workers: int

    def to_record(self) -> dict[str, Any]:
        return asdict(self)



def collect_runtime_metrics(
    *,
    project_root: Path,
) -> RuntimeMetricsSnapshot:
    daemon_store = RuntimeDaemonStateStore(
        project_root=project_root,
    )

    daemon_state = daemon_store.read_resolved()
    runtime_health = evaluate_runtime_health(daemon_state)

    backoff = RestartBackoffStore(
        project_root=project_root,
    ).read()

    worker_health = RuntimeWorkerHealthStore(
        project_root=project_root,
    ).read_all()

    quarantine = RuntimeWorkerQuarantineStore(
        project_root=project_root,
    ).read_all()

    healthy_workers = 0
    failed_workers = 0

    for worker in worker_health.values():
        if worker.status == 'healthy':
            healthy_workers += 1

        elif worker.status == 'failed':
            failed_workers += 1

    return RuntimeMetricsSnapshot(
        runtime_state=daemon_state.state,
        runtime_health=runtime_health.status,
        runtime_health_score=runtime_health.score,
        restart_count=int(backoff.get('restart_count') or 0),
        worker_count=len(worker_health),
        quarantined_workers=len(quarantine),
        healthy_workers=healthy_workers,
        failed_workers=failed_workers,
    )
