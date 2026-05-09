import json
import threading
import urllib.request
from pathlib import Path

from runtime.metrics_server import RuntimeMetricsHttpServer



def test_runtime_metrics_http_server_exports_metrics(
    tmp_path: Path,
):
    server = RuntimeMetricsHttpServer(
        ('127.0.0.1', 0),
        project_root=tmp_path,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    host, port = server.server_address

    response = urllib.request.urlopen(
        f'http://{host}:{port}/metrics'
    )

    payload = json.loads(
        response.read().decode('utf-8')
    )

    server.shutdown()
    server.server_close()

    assert 'runtime_state' in payload
    assert 'runtime_health' in payload



def test_runtime_metrics_http_server_returns_404(
    tmp_path: Path,
):
    server = RuntimeMetricsHttpServer(
        ('127.0.0.1', 0),
        project_root=tmp_path,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    host, port = server.server_address

    try:
        urllib.request.urlopen(
            f'http://{host}:{port}/unknown'
        )

        assert False

    except Exception as error:
        assert '404' in str(error)

    server.shutdown()
    server.server_close()
