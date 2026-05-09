from __future__ import annotations

from dataclasses import dataclass

from imessage.watcher import IMessageWatcher
from room.models import RoomEvent, RoomEventType


@dataclass
class IMessageWatchWorkerResult:
    accepted: int
    rejected: int


class IMessageWatchWorker:
    def __init__(
        self,
        *,
        watcher: IMessageWatcher,
        dry_run: bool = False,
    ) -> None:
        self.watcher = watcher
        self.dry_run = dry_run

    def handle(self, event: RoomEvent) -> IMessageWatchWorkerResult:
        if event.type is not RoomEventType.SYSTEM_MESSAGE:
            return IMessageWatchWorkerResult(
                accepted=0,
                rejected=0,
            )

        if event.target not in {'imessage-watch', 'watcher'}:
            return IMessageWatchWorkerResult(
                accepted=0,
                rejected=0,
            )

        decisions = self.watcher.poll_once(dry_run=self.dry_run)

        accepted = sum(1 for decision in decisions if decision.accepted)
        rejected = len(decisions) - accepted

        return IMessageWatchWorkerResult(
            accepted=accepted,
            rejected=rejected,
        )
