from runtime.state_machine import (
    RuntimeLifecycleEvent,
    RuntimeLifecycleState,
    RuntimeLifecycleStateMachine,
    RuntimeLifecycleTransitionError,
    map_runtime_health_to_lifecycle_state,
)



def test_runtime_state_machine_start_flow():
    machine = RuntimeLifecycleStateMachine()

    assert machine.state == RuntimeLifecycleState.STOPPED

    machine.transition(
        RuntimeLifecycleEvent.START_REQUESTED,
    )

    machine.transition(
        RuntimeLifecycleEvent.STARTED,
    )

    assert machine.state == RuntimeLifecycleState.RUNNING



def test_runtime_state_machine_recovery_flow():
    machine = RuntimeLifecycleStateMachine(
        state=RuntimeLifecycleState.RUNNING,
    )

    machine.transition(
        RuntimeLifecycleEvent.HEALTH_DEGRADED,
    )

    assert machine.state == RuntimeLifecycleState.DEGRADED

    machine.transition(
        RuntimeLifecycleEvent.RECOVERY_REQUESTED,
    )

    assert machine.state == RuntimeLifecycleState.RECOVERING

    machine.transition(
        RuntimeLifecycleEvent.RECOVERED,
    )

    assert machine.state == RuntimeLifecycleState.RUNNING



def test_runtime_state_machine_stop_flow():
    machine = RuntimeLifecycleStateMachine(
        state=RuntimeLifecycleState.RUNNING,
    )

    machine.transition(
        RuntimeLifecycleEvent.STOP_REQUESTED,
    )

    assert machine.state == RuntimeLifecycleState.STOPPING

    machine.transition(
        RuntimeLifecycleEvent.STOPPED,
    )

    assert machine.state == RuntimeLifecycleState.STOPPED



def test_runtime_state_machine_rejects_invalid_transition():
    machine = RuntimeLifecycleStateMachine()

    raised = False

    try:
        machine.transition(
            RuntimeLifecycleEvent.RECOVERED,
        )

    except RuntimeLifecycleTransitionError:
        raised = True

    assert raised is True



def test_runtime_state_machine_can_transition_checks():
    machine = RuntimeLifecycleStateMachine()

    assert machine.can_transition(
        RuntimeLifecycleEvent.START_REQUESTED,
    ) is True

    assert machine.can_transition(
        RuntimeLifecycleEvent.RECOVERED,
    ) is False



def test_map_runtime_health_to_running_state():
    result = map_runtime_health_to_lifecycle_state(
        runtime_state='running',
        health_status='healthy',
    )

    assert result == RuntimeLifecycleState.RUNNING



def test_map_runtime_health_to_degraded_state():
    result = map_runtime_health_to_lifecycle_state(
        runtime_state='running',
        health_status='stale',
    )

    assert result == RuntimeLifecycleState.DEGRADED



def test_map_runtime_health_to_failed_state():
    result = map_runtime_health_to_lifecycle_state(
        runtime_state='running',
        health_status='unknown',
    )

    assert result == RuntimeLifecycleState.FAILED
