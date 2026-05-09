from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from runtime.metrics import collect_runtime_metrics


class RuntimeMetricsHandler(BaseHTTPRequestHandler):
    project_root: Path

    def do_GET(self) -> None:
        if self.path != '/metrics':
            self.send_response(404)
            self.end_headers()
            return

        metrics = collect_runtime_metrics(
            project_root=self.project_root,
        )

        payload = json.dumps(
            metrics.to_record(),
            indent=2,
            sort_keys=True,
        ).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


class RuntimeMetricsHttpServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address,
        *,
        project_root: Path,
    ):
        handler = type(
            'BoundRuntimeMetricsHandler',
            (RuntimeMetricsHandler,),
            {
                'project_root': project_root,
            },
        )

        super().__init__(server_address, handler)


def run_metrics_http_server(
    *,
    project_root: Path,
    host: str = '127.0.0.1',
    port: int = 8787,
) -> RuntimeMetricsHttpServer:
    server = RuntimeMetricsHttpServer(
        (host, port),
        project_root=project_root,
    )

    server.serve_forever()
    return server
