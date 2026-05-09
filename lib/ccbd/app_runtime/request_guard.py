from __future__ import annotations

from typing import Optional

_STOPPING_GUARDED_OPS = frozenset({
    'submit',
    'attach',
    'start',
    'restore',
    'cancel',
    'ack',
    'resubmit',
    'retry',
})


def rejection_for_request(app, op: str) -> Optional[str]:
    if op not in _STOPPING_GUARDED_OPS:
        return None
    try:
        lifecycle = app.lifecycle_store.load()
    except Exception:
        lifecycle = None
    if lifecycle is None:
        return None
    phase = str(getattr(lifecycle, 'phase', '') or '').strip()
    desired_state = str(getattr(lifecycle, 'desired_state', '') or '').strip()
    shutdown_intent = str(getattr(lifecycle, 'shutdown_intent', '') or '').strip()
    if phase == 'stopping':
        return 'ccbd is unavailable: lifecycle_stopping'
    if desired_state == 'stopped' and shutdown_intent:
        return 'ccbd is unavailable: lifecycle_stopping'
    return None


__all__ = ['rejection_for_request']
