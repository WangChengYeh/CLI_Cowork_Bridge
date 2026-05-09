import signal

from runtime.signals import (
    RuntimeSignalStopFlag,
    install_runtime_signal_handlers,
)


class FakeSignalModule:
    def __init__(self):
        self.handlers = {}

    def getsignal(self, signum):
        return self.handlers.get(signum)

    def signal(self, signum, handler):
        self.handlers[signum] = handler



def test_signal_stop_flag_records_signal():
    stop_flag = RuntimeSignalStopFlag()

    stop_flag.request_stop(signal.SIGINT)

    assert stop_flag.should_stop() is True
    assert signal.SIGINT in stop_flag.received_signals



def test_install_runtime_signal_handlers_registers_handlers():
    fake_signal = FakeSignalModule()
    stop_flag = RuntimeSignalStopFlag()

    previous = install_runtime_signal_handlers(
        stop_flag,
        signal_module=fake_signal,
    )

    assert signal.SIGINT in fake_signal.handlers
    assert signal.SIGTERM in fake_signal.handlers
    assert isinstance(previous, dict)



def test_registered_signal_handler_triggers_stop():
    fake_signal = FakeSignalModule()
    stop_flag = RuntimeSignalStopFlag()

    install_runtime_signal_handlers(
        stop_flag,
        signal_module=fake_signal,
    )

    handler = fake_signal.handlers[signal.SIGTERM]

    handler(signal.SIGTERM, None)

    assert stop_flag.should_stop() is True
    assert signal.SIGTERM in stop_flag.received_signals
