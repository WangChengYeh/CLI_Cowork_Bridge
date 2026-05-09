from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from room.imessage_delivery import RoomIMessageDelivery
from room.models import RoomEvent, RoomEventType


DELIVERABLE_EVENT_TYPES = {
    RoomEventType.AGENT_MESSAGE,
    RoomEventType.TASK_COMPLETED,
    RoomEventType.TASK_FAILED,
    RoomEventType.APPROVAL_NEEDED,
}


@dataclass
class DeliveryWorkerResult:
    attempted: bool
    delivered: bool
    reason: Optional[str] = None


class DeliveryWorker:
    def __init__(
        self,
        *,
        delivery: RoomIMessageDelivery,
        dry_run: bool = False,
    ) -> None:
        self.delivery = delivery
        self.dry_run = dry_run

    def handle(self, event: RoomEvent) -> DeliveryWorkerResult:
        if event.type not in DELIVERABLE_EVENT_TYPES:
            return DeliveryWorkerResult(
                attempted=False,
                delivered=False,
                reason='event type not deliverable',
            )

        result = self.delivery.deliver(event, dry_run=self.dry_run)

        return DeliveryWorkerResult(
            attempted=True,
            delivered=result.delivered,
            reason=result.reason,
        )
