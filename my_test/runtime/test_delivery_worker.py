from room.models import RoomEvent, RoomEventType, RoomSource
from runtime.workers.delivery_worker import DeliveryWorker


class FakeDelivery:
    def __init__(self):
        self.calls = []

    def deliver(self, event, dry_run=False):
        self.calls.append(
            {
                'event': event,
                'dry_run': dry_run,
            }
        )

        class Result:
            delivered = True
            reason = None

        return Result()



def make_event(event_type: RoomEventType) -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.AGENT,
        sender='codex',
        target='you',
        type=event_type,
        body='streamed reply',
    )


def test_delivery_worker_delivers_agent_message():
    delivery = FakeDelivery()

    worker = DeliveryWorker(
        delivery=delivery,
        dry_run=True,
    )

    result = worker.handle(
        make_event(RoomEventType.AGENT_MESSAGE)
    )

    assert result.attempted is True
    assert result.delivered is True
    assert len(delivery.calls) == 1
    assert delivery.calls[0]['dry_run'] is True


def test_delivery_worker_delivers_task_failed():
    delivery = FakeDelivery()

    worker = DeliveryWorker(
        delivery=delivery,
    )

    result = worker.handle(
        make_event(RoomEventType.TASK_FAILED)
    )

    assert result.attempted is True
    assert result.delivered is True


def test_non_deliverable_event_is_skipped():
    delivery = FakeDelivery()

    worker = DeliveryWorker(
        delivery=delivery,
    )

    result = worker.handle(
        make_event(RoomEventType.USER_MESSAGE)
    )

    assert result.attempted is False
    assert result.delivered is False
    assert len(delivery.calls) == 0
