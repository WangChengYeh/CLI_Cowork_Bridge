import json
import urllib.request
from pathlib import Path

from runtime.metrics_runtime import start_metrics_runtime



def test_metrics_runtime_serves_metrics(
    tmp_path: Path,
):
    runtime = start_metrics_runtime(
        project_root=tmp_path,
        port=0,
    )

    host, port = runtime.server.server_address

    response = urllib.request.urlopen(
        f'http://{host}:{port}/metrics'
    )

    payload = json.loads(
        response.read().decode('utf-8')
    )

    runtime.stop()

    assert 'runtime_state' in payload



def test_metrics_runtime_stops_cleanly(
    tmp_path: Path,
):
    runtime = start_metrics_runtime(
        project_root=tmp_path,
        port=0,
    )

    runtime.stop()

    assert runtime.thread.is_alive() is False
