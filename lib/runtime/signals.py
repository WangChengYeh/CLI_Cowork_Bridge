from __future__ import annotations

import signal
from dataclasses import dataclass, field
from types import FrameType
from typing import Callable, Optional


SignalHandler = Callable[[int, Optional[FrameType]], None]


@dataclass
class RuntimeSignalStopFlag:
    requested: bool = False
    received_signals: list[int] = field(default_factory=list)

    def request_stop(self, signum: int, frame: Optional[FrameType] = None) -> None:
        del frame
        self.requested = True
        self.received_signals.append(signum)

    def should_stop(self) -> bool:
        return self.requested


def install_runtime_signal_handlers(
    stop_flag: RuntimeSignalStopFlag,
    *,
    signal_module=signal,
) -> dict[int, SignalHandler]:
    previous_handlers: dict[int, SignalHandler] = {}

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous = signal_module.getsignal(signum)
        previous_handlers[signum] = previous
        signal_module.signal(signum, stop_flag.request_stop)

    return previous_handlers
