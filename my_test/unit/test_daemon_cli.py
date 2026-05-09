from io import StringIO
from pathlib import Path

from cli.daemon_cli import run_daemon_cli
from runtime.background import (
    BackgroundDaemonRestartResult,
    BackgroundDaemonStopResult,
)
from runtime.health import RuntimeHealth
from runtime.watchdog import RuntimeWatchdogLoopResult, RuntimeWatchdogTickResult



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
    assert 'lifecycle_state=' in output
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

    from runtime.daemon_runner import RuntimeDaemonRunResult

    def fake_run_forever(*args, **kwargs):
        return RuntimeDaemonRunResult(
            iterations=1,
            processed_events=0,
            stopped_by_condition=False,
        )

    result = run_daemon_cli(
        ['start', '--foreground'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
        run_runtime_forever_fn=fake_run_forever,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'running' in output
    assert 'foreground_iterations=' in output



def test_daemon_stop_reports_stopped(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    def fake_stop_daemon(*, project_root):
        return BackgroundDaemonStopResult(
            signaled=False,
            pid=None,
            reason='not-running',
        )

    result = run_daemon_cli(
        ['stop'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
        stop_daemon_fn=fake_stop_daemon,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'stopped' in output
    assert 'signaled=' in output



def test_daemon_restart_reports_recovery_state(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    def fake_restart_daemon(*, project_root):
        return BackgroundDaemonRestartResult(
            restarted=False,
            launch=None,
            reason='already-running',
        )

    result = run_daemon_cli(
        ['restart'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
        restart_daemon_fn=fake_restart_daemon,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'restarted=' in output



def test_daemon_metrics_exports_json(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_daemon_cli(
        ['metrics'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'runtime_state' in output
    assert 'runtime_health' in output



def test_daemon_watchdog_reports_health(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    def fake_watchdog_tick(*, project_root):
        return RuntimeWatchdogTickResult(
            runtime_state='stopped',
            health=RuntimeHealth(
                status='stopped',
                score=0,
                reason='not-running',
            ),
            restarted=False,
        )

    result = run_daemon_cli(
        ['watchdog'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
        run_watchdog_tick_fn=fake_watchdog_tick,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'health_status=' in output
    assert 'lifecycle_state=stopped' in output
    assert 'restarted=' in output



def test_daemon_watchdog_loop_reports_iterations(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    def fake_watchdog_loop(*, project_root, max_iterations):
        return RuntimeWatchdogLoopResult(
            iterations=max_iterations,
            restarts=0,
            last_tick=RuntimeWatchdogTickResult(
                runtime_state='stopped',
                health=RuntimeHealth(
                    status='stopped',
                    score=0,
                    reason='not-running',
                ),
                restarted=False,
            ),
        )

    result = run_daemon_cli(
        ['watchdog', '--loop', '--iterations', '2'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
        run_watchdog_loop_fn=fake_watchdog_loop,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'watchdog_iterations=2' in output
    assert 'watchdog_restarts=' in output
    assert 'lifecycle_state=' in output
