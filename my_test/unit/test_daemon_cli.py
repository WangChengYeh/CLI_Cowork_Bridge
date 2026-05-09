from io import StringIO
from pathlib import Path

from cli.daemon_cli import run_daemon_cli



def test_daemon_status_prints_runtime_fields(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['status'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'worker_count=' in output
    assert 'cursor_name=' in output



def test_daemon_poll_once_reports_processed_events(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['poll-once'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'processed_events=' in output
    assert 'next_offset=' in output



def test_daemon_start_foreground_reports_running(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['start', '--foreground'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'running' in output
    assert 'foreground_iterations=' in output



def test_daemon_stop_reports_stopped(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['stop'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'stopped' in output
    assert 'signaled=' in output



def test_daemon_restart_reports_recovery_state(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['restart'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'restarted=' in output



def test_daemon_watchdog_reports_health(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['watchdog'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'health_status=' in output
    assert 'restarted=' in output
