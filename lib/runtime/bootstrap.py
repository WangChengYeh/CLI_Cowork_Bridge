from __future__ import annotations

from typing import Optional

from dataclasses import dataclass
from pathlib import Path

from imessage.watcher import IMessageWatcher
from room.imessage_delivery import (
    RoomIMessageDelivery,
    RoomIMessageDeliveryPolicy,
)
from room.store import RoomEventStore
from runtime.event_loop import RuntimeEventLoop
from runtime.supervisor import RuntimeSupervisor
from runtime.worker import RuntimeWorker
from runtime.workers.delivery_worker import DeliveryWorker
from runtime.workers.dispatch_worker import DispatchWorker
from runtime.workers.imessage_watch_worker import IMessageWatchWorker


DEFAULT_PARTICIPANTS = {
    'codex',
    'claude',
    'gemini',
}


@dataclass
class RuntimeBootstrap:
    project_root: Path
    store: RoomEventStore
    supervisor: RuntimeSupervisor
    dispatch_worker: DispatchWorker
    delivery_worker: DeliveryWorker
    watch_worker: IMessageWatchWorker
    delivery: RoomIMessageDelivery
    watcher: IMessageWatcher


def bootstrap_runtime(
    *,
    project_root: Path,
    enable_imessage: bool = False,
    imessage_allow_senders: Optional[set[str]] = None,
) -> RuntimeBootstrap:
    project_root = Path(project_root)

    store = RoomEventStore(project_root / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=project_root,
        store=store,
        event_loop=RuntimeEventLoop(
            project_root=project_root,
            store=store,
            cursor_name='runtime-supervisor',
        ),
    )

    dispatch_worker = DispatchWorker(
        project_root=project_root,
        store=store,
    )

    supervisor.register_worker(
        RuntimeWorker(
            name='dispatch-worker',
            handler=dispatch_worker.handle,
        )
    )

    delivery = RoomIMessageDelivery(
        project_root=project_root,
        store=store,
        policy=RoomIMessageDeliveryPolicy(
            enabled=enable_imessage,
            recipients=[],
        ),
    )

    delivery_worker = DeliveryWorker(
        delivery=delivery,
        dry_run=True,
    )

    supervisor.register_worker(
        RuntimeWorker(
            name='delivery-worker',
            handler=delivery_worker.handle,
        )
    )

    watcher = IMessageWatcher(
        project_root=project_root,
        allow_senders=imessage_allow_senders or set(),
        participants=DEFAULT_PARTICIPANTS,
        store=store,
    )

    watch_worker = IMessageWatchWorker(
        watcher=watcher,
        dry_run=True,
    )

    supervisor.register_worker(
        RuntimeWorker(
            name='imessage-watch-worker',
            handler=watch_worker.handle,
        )
    )

    return RuntimeBootstrap(
        project_root=project_root,
        store=store,
        supervisor=supervisor,
        dispatch_worker=dispatch_worker,
        delivery_worker=delivery_worker,
        watch_worker=watch_worker,
        delivery=delivery,
        watcher=watcher,
    )
