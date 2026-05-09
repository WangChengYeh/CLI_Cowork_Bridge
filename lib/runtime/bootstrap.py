from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from room.imessage_delivery import (
    RoomIMessageDelivery,
    RoomIMessageDeliveryPolicy,
)
from room.store import RoomEventStore
from runtime.event_loop import RuntimeEventLoop
from runtime.supervisor import RuntimeSupervisor
from runtime.worker import RuntimeWorker
from runtime.workers.dispatch_worker import DispatchWorker


@dataclass(slots=True)
class RuntimeBootstrap:
    project_root: Path
    store: RoomEventStore
    supervisor: RuntimeSupervisor
    dispatch_worker: DispatchWorker
    delivery: RoomIMessageDelivery


def bootstrap_runtime(
    *,
    project_root: Path,
    enable_imessage: bool = False,
) -> RuntimeBootstrap:
    project_root = Path(project_root)

    store = RoomEventStore(project_root / '.ccb' / 'room')

    supervisor = RuntimeSupervisor(
        project_root=project_root,
        store=store,
        event_loop=RuntimeEventLoop(
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

    return RuntimeBootstrap(
        project_root=project_root,
        store=store,
        supervisor=supervisor,
        dispatch_worker=dispatch_worker,
        delivery=delivery,
    )
