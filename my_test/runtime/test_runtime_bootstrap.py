from pathlib import Path

from runtime.bootstrap import bootstrap_runtime



def test_bootstrap_creates_shared_runtime_components(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
    )

    assert runtime.store is not None
    assert runtime.supervisor is not None
    assert runtime.dispatch_worker is not None
    assert runtime.delivery is not None


def test_bootstrap_registers_dispatch_worker(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
    )

    workers = runtime.supervisor.registry.workers

    assert 'dispatch-worker' in workers


def test_bootstrap_respects_imessage_flag(tmp_path: Path):
    runtime = bootstrap_runtime(
        project_root=tmp_path,
        enable_imessage=True,
    )

    assert runtime.delivery.policy.enabled is True
