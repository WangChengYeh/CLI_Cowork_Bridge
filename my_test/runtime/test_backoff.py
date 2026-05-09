from pathlib import Path

from runtime.backoff import (
    RestartBackoffPolicy,
    RestartBackoffStore,
    evaluate_restart_backoff,
)



def test_restart_backoff_allows_initial_restart(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    decision = evaluate_restart_backoff(store=store)

    assert decision.allowed is True



def test_restart_backoff_blocks_after_limit(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    store.record_restart()
    store.record_restart()
    store.record_restart()

    decision = evaluate_restart_backoff(
        store=store,
        policy=RestartBackoffPolicy(max_restarts=3),
    )

    assert decision.allowed is False



def test_restart_backoff_reset_clears_restart_count(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    store.record_restart()
    store.reset()

    decision = evaluate_restart_backoff(store=store)

    assert decision.allowed is True
    assert decision.restart_count == 0
