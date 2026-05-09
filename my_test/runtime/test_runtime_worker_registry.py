from room.models import RoomEvent, RoomEventType, RoomSource
from runtime.worker import RuntimeWorker, RuntimeWorkerRegistry


def make_event() -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.CLI,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
    )


def test_register_worker_by_name():
    registry = RuntimeWorkerRegistry()

    registry.register(
        RuntimeWorker(
            name='worker-1',
            handler=lambda event: None,
        )
    )

    assert 'worker-1' in registry.workers


def test_dispatch_calls_enabled_worker():
    registry = RuntimeWorkerRegistry()
    seen = []

    registry.register(
        RuntimeWorker(
            name='collector',
            handler=seen.append,
        )
    )

    event = make_event()
    registry.dispatch(event)

    assert seen == [event]


def test_disabled_worker_is_skipped():
    registry = RuntimeWorkerRegistry()
    seen = []

    registry.register(
        RuntimeWorker(
            name='collector',
            handler=seen.append,
            enabled=False,
        )
    )

    registry.dispatch(make_event())

    assert seen == []


def test_multiple_workers_receive_same_event():
    registry = RuntimeWorkerRegistry()
    seen_a = []
    seen_b = []

    registry.register(RuntimeWorker(name='a', handler=seen_a.append))
    registry.register(RuntimeWorker(name='b', handler=seen_b.append))

    event = make_event()
    registry.dispatch(event)

    assert seen_a == [event]
    assert seen_b == [event]


def test_register_same_name_replaces_worker():
    registry = RuntimeWorkerRegistry()
    seen_a = []
    seen_b = []

    registry.register(RuntimeWorker(name='same', handler=seen_a.append))
    registry.register(RuntimeWorker(name='same', handler=seen_b.append))

    event = make_event()
    registry.dispatch(event)

    assert seen_a == []
    assert seen_b == [event]
