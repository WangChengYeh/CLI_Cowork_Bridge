from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path

from runtime.metrics_server import RuntimeMetricsHttpServer


@dataclass
class RuntimeMetricsRuntime:
    server: RuntimeMetricsHttpServer
    thread: threading.Thread

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)



def start_metrics_runtime(
    *,
    project_root: Path,
    host: str = '127.0.0.1',
    port: int = 8787,
) -> RuntimeMetricsRuntime:
    server = RuntimeMetricsHttpServer(
        (host, port),
        project_root=project_root,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
        name='ccb-metrics-runtime',
    )

    thread.start()

    return RuntimeMetricsRuntime(
        server=server,
        thread=thread,
    )
