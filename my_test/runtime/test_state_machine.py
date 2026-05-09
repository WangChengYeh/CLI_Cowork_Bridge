from runtime.state_machine import (
    RuntimeLifecycleEvent,
    RuntimeLifecycleState,
    RuntimeLifecycleStateMachine,
    RuntimeLifecycleTransitionError,
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

    try:
        machine.transition(
            RuntimeLifecycleEvent.RECOVERED,
        )

        assert False

    except RuntimeLifecycleTransitionError:
        assert True



def test_runtime_state_machine_can_transition_checks():
    machine = RuntimeLifecycleStateMachine()

    assert machine.can_transition(
        RuntimeLifecycleEvent.START_REQUESTED,
    ) is True

    assert machine.can_transition(
        RuntimeLifecycleEvent.RECOVERED,
    ) is False
