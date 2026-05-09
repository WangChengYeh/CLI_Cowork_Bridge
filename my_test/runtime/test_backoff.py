from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime.backoff import (
    RestartBackoffPolicy,
    RestartBackoffStore,
    evaluate_restart_backoff,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)



def test_restart_backoff_allows_initial_restart(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    decision = evaluate_restart_backoff(store=store)

    assert decision.allowed is True



def test_restart_backoff_blocks_after_limit(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    store.record_restart(now=NOW)
    store.record_restart(now=NOW)
    store.record_restart(now=NOW)

    decision = evaluate_restart_backoff(
        store=store,
        policy=RestartBackoffPolicy(max_restarts=3),
        now=NOW,
    )

    assert decision.allowed is False



def test_restart_backoff_reset_clears_restart_count(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    store.record_restart(now=NOW)
    store.reset()

    decision = evaluate_restart_backoff(
        store=store,
        now=NOW,
    )

    assert decision.allowed is True
    assert decision.restart_count == 0



def test_restart_backoff_window_decay_resets_old_budget(tmp_path: Path):
    store = RestartBackoffStore(project_root=tmp_path)

    old = NOW - timedelta(seconds=600)

    store.record_restart(now=old)
    store.record_restart(now=old)
    store.record_restart(now=old)

    decision = evaluate_restart_backoff(
        store=store,
        policy=RestartBackoffPolicy(
            max_restarts=3,
            window_seconds=300,
        ),
        now=NOW,
    )

    assert decision.allowed is True
    assert decision.restart_count == 0
