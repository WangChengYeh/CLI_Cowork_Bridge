from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RuntimeLifecycleState(StrEnum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    RUNNING = 'running'
    DEGRADED = 'degraded'
    RECOVERING = 'recovering'
    STOPPING = 'stopping'
    FAILED = 'failed'


class RuntimeLifecycleEvent(StrEnum):
    START_REQUESTED = 'start_requested'
    STARTED = 'started'
    HEALTH_DEGRADED = 'health_degraded'
    RECOVERY_REQUESTED = 'recovery_requested'
    RECOVERED = 'recovered'
    STOP_REQUESTED = 'stop_requested'
    STOPPED = 'stopped'
    FAILED = 'failed'


class RuntimeLifecycleTransitionError(ValueError):
    pass


TRANSITIONS: dict[
    RuntimeLifecycleState,
    dict[RuntimeLifecycleEvent, RuntimeLifecycleState],
] = {
    RuntimeLifecycleState.STOPPED: {
        RuntimeLifecycleEvent.START_REQUESTED: RuntimeLifecycleState.STARTING,
    },
    RuntimeLifecycleState.STARTING: {
        RuntimeLifecycleEvent.STARTED: RuntimeLifecycleState.RUNNING,
        RuntimeLifecycleEvent.FAILED: RuntimeLifecycleState.FAILED,
        RuntimeLifecycleEvent.STOP_REQUESTED: RuntimeLifecycleState.STOPPING,
    },
    RuntimeLifecycleState.RUNNING: {
        RuntimeLifecycleEvent.HEALTH_DEGRADED: RuntimeLifecycleState.DEGRADED,
        RuntimeLifecycleEvent.RECOVERY_REQUESTED: RuntimeLifecycleState.RECOVERING,
        RuntimeLifecycleEvent.STOP_REQUESTED: RuntimeLifecycleState.STOPPING,
        RuntimeLifecycleEvent.FAILED: RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.DEGRADED: {
        RuntimeLifecycleEvent.RECOVERY_REQUESTED: RuntimeLifecycleState.RECOVERING,
        RuntimeLifecycleEvent.RECOVERED: RuntimeLifecycleState.RUNNING,
        RuntimeLifecycleEvent.STOP_REQUESTED: RuntimeLifecycleState.STOPPING,
        RuntimeLifecycleEvent.FAILED: RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.RECOVERING: {
        RuntimeLifecycleEvent.RECOVERED: RuntimeLifecycleState.RUNNING,
        RuntimeLifecycleEvent.HEALTH_DEGRADED: RuntimeLifecycleState.DEGRADED,
        RuntimeLifecycleEvent.STOP_REQUESTED: RuntimeLifecycleState.STOPPING,
        RuntimeLifecycleEvent.FAILED: RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.STOPPING: {
        RuntimeLifecycleEvent.STOPPED: RuntimeLifecycleState.STOPPED,
        RuntimeLifecycleEvent.FAILED: RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.FAILED: {
        RuntimeLifecycleEvent.RECOVERY_REQUESTED: RuntimeLifecycleState.RECOVERING,
        RuntimeLifecycleEvent.STOP_REQUESTED: RuntimeLifecycleState.STOPPING,
    },
}


@dataclass(slots=True)
class RuntimeLifecycleStateMachine:
    state: RuntimeLifecycleState = RuntimeLifecycleState.STOPPED

    def transition(
        self,
        event: RuntimeLifecycleEvent,
    ) -> RuntimeLifecycleState:
        next_state = TRANSITIONS.get(self.state, {}).get(event)

        if next_state is None:
            raise RuntimeLifecycleTransitionError(
                f'invalid runtime lifecycle transition: '
                f'{self.state.value} + {event.value}'
            )

        self.state = next_state
        return self.state

    def can_transition(self, event: RuntimeLifecycleEvent) -> bool:
        return event in TRANSITIONS.get(self.state, {})


def map_runtime_health_to_lifecycle_state(
    *,
    runtime_state: str,
    health_status: str,
) -> RuntimeLifecycleState:
    if runtime_state == 'stopped':
        return RuntimeLifecycleState.STOPPED

    if health_status == 'healthy':
        return RuntimeLifecycleState.RUNNING

    if health_status == 'stale':
        return RuntimeLifecycleState.DEGRADED

    if health_status == 'stopped':
        return RuntimeLifecycleState.STOPPED

    if health_status == 'unknown':
        return RuntimeLifecycleState.FAILED

    return RuntimeLifecycleState.FAILED
