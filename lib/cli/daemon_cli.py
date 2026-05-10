from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, TextIO

from runtime.background import (
    launch_background_daemon,
    restart_background_daemon_if_needed,
    stop_background_daemon,
)
from runtime.bootstrap import bootstrap_runtime
from runtime.daemon_runner import run_runtime_forever
from runtime.daemon_state import (
    RuntimeDaemonAlreadyRunning,
    RuntimeDaemonStateStore,
)
from runtime.health import evaluate_runtime_health
from runtime.metrics import collect_runtime_metrics
from runtime.signals import (
    RuntimeSignalStopFlag,
    install_runtime_signal_handlers,
)
from runtime.state_machine import map_runtime_health_to_lifecycle_state
from runtime.watchdog import (
    run_watchdog_loop,
    run_watchdog_tick,
)


STATE_STOPPED = 'stopped'
STATE_RUNNING = 'running'


DEFAULT_WATCHDOG_ITERATIONS = 1


def build_daemon_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='ccb daemon')
    subparsers = parser.add_subparsers(dest='command', required=True)

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('--foreground', action='store_true')
    start_parser.add_argument('--iterations', type=int, default=None)
    start_parser.add_argument('--imessage', action='store_true')
    start_parser.add_argument('--recipients', nargs='+', default=[])

    subparsers.add_parser('stop')
    subparsers.add_parser('restart')
    subparsers.add_parser('metrics')

    watchdog_parser = subparsers.add_parser('watchdog')
    watchdog_parser.add_argument('--loop', action='store_true')
    watchdog_parser.add_argument(
        '--iterations',
        type=int,
        default=DEFAULT_WATCHDOG_ITERATIONS,
    )

    subparsers.add_parser('status')
    subparsers.add_parser('poll-once')

    return parser


def run_daemon_cli(
    argv: list[str],
    *,
    project_root: Path,
    stdout: TextIO,
    stderr: TextIO,
    launch_daemon_fn: Callable = launch_background_daemon,
    stop_daemon_fn: Callable = stop_background_daemon,
    restart_daemon_fn: Callable = restart_background_daemon_if_needed,
    run_watchdog_tick_fn: Callable = run_watchdog_tick,
    run_watchdog_loop_fn: Callable = run_watchdog_loop,
    bootstrap_fn: Callable = bootstrap_runtime,
    run_runtime_forever_fn: Callable = run_runtime_forever,
) -> int:
    parser = build_daemon_parser()
    args = parser.parse_args(argv)

    daemon_state = RuntimeDaemonStateStore(project_root=project_root)

    if args.command == 'start':
        try:
            if not args.foreground:
                background_argv = list(argv)
                if '--foreground' not in background_argv:
                    background_argv.append('--foreground')

                ccb_path = project_root / 'ccb'
                if ccb_path.exists():
                    full_argv = [str(ccb_path), 'daemon'] + background_argv
                else:
                    full_argv = [sys.executable, '-m', 'cli.daemon_cli'] + background_argv

                launch = launch_daemon_fn(
                    project_root=project_root,
                    argv=full_argv,
                )

                stdout.write(f'{STATE_RUNNING}\n')
                stdout.write(f'pid={launch.pid}\n')
                stdout.write(f'log_path={launch.log_path}\n')
                return 0

            state = daemon_state.mark_running(force=True)
        except RuntimeDaemonAlreadyRunning as error:
            stderr.write(f'{error}\n')
            return 1

        stdout.write(f'{state.state}\n')
        stdout.write(f'pid={state.pid}\n')

        runtime = bootstrap_fn(
            project_root=project_root,
            enable_imessage=args.imessage,
            imessage_allow_senders=set(args.recipients),
        )

        # If we have recipients, we probably want to actually send
        if args.recipients:
            runtime.delivery.policy.recipients = args.recipients
            runtime.delivery_worker.dry_run = False
            runtime.watch_worker.dry_run = False

        stop_flag = RuntimeSignalStopFlag()
        install_runtime_signal_handlers(stop_flag)

        result = run_runtime_forever_fn(
            project_root=project_root,
            bootstrap=runtime,
            max_iterations=args.iterations,
            should_stop=stop_flag.should_stop,
        )

        stdout.write(f'foreground_iterations={result.iterations}\n')
        stdout.write(f'foreground_processed_events={result.processed_events}\n')
        stdout.write(f'foreground_stopped={result.stopped_by_condition}\n')
        return 0

    if args.command == 'stop':
        result = stop_daemon_fn(project_root=project_root)

        stdout.write(f'{STATE_STOPPED}\n')
        stdout.write(f'signaled={result.signaled}\n')
        stdout.write(f'pid={result.pid}\n')

        if result.reason is not None:
            stdout.write(f'reason={result.reason}\n')

        return 0

    if args.command == 'restart':
        result = restart_daemon_fn(project_root=project_root)

        stdout.write(f'restarted={result.restarted}\n')

        if result.launch is not None:
            stdout.write(f'pid={result.launch.pid}\n')
            stdout.write(f'log_path={result.launch.log_path}\n')

        if result.reason is not None:
            stdout.write(f'reason={result.reason}\n')

        return 0

    if args.command == 'metrics':
        metrics = collect_runtime_metrics(project_root=project_root)
        stdout.write(json.dumps(metrics.to_record(), indent=2, sort_keys=True))
        stdout.write('\n')
        return 0

    if args.command == 'watchdog':
        if args.loop:
            result = run_watchdog_loop_fn(
                project_root=project_root,
                max_iterations=args.iterations,
            )

            stdout.write(f'watchdog_iterations={result.iterations}\n')
            stdout.write(f'watchdog_restarts={result.restarts}\n')

            if result.last_tick is not None:
                lifecycle_state = map_runtime_health_to_lifecycle_state(
                    runtime_state=result.last_tick.runtime_state,
                    health_status=result.last_tick.health.status,
                )
                stdout.write(f'health_status={result.last_tick.health.status}\n')
                stdout.write(f'lifecycle_state={lifecycle_state.value}\n')

            return 0

        result = run_watchdog_tick_fn(project_root=project_root)
        lifecycle_state = map_runtime_health_to_lifecycle_state(
            runtime_state=result.runtime_state,
            health_status=result.health.status,
        )

        stdout.write(f'health_status={result.health.status}\n')
        stdout.write(f'lifecycle_state={lifecycle_state.value}\n')
        stdout.write(f'health_score={result.health.score}\n')
        stdout.write(f'health_reason={result.health.reason}\n')
        stdout.write(f'restarted={result.restarted}\n')

        if result.restart is not None and result.restart.launch is not None:
            stdout.write(f'pid={result.restart.launch.pid}\n')
            stdout.write(f'log_path={result.restart.launch.log_path}\n')

        return 0

    # These commands need a supervisor, so we bootstrap a minimal one
    runtime = bootstrap_runtime(project_root=project_root)
    supervisor = runtime.supervisor

    if args.command == 'status':
        runtime_status = supervisor.status()
        daemon_runtime_state = daemon_state.read_resolved()
        health = evaluate_runtime_health(daemon_runtime_state)
        lifecycle_state = map_runtime_health_to_lifecycle_state(
            runtime_state=daemon_runtime_state.state,
            health_status=health.status,
        )

        stdout.write(f'state={daemon_runtime_state.state}\n')
        stdout.write(f'lifecycle_state={lifecycle_state.value}\n')
        stdout.write(f'pid={daemon_runtime_state.pid}\n')
        stdout.write(f'worker_count={runtime_status.worker_count}\n')
        stdout.write(f'cursor_name={runtime_status.cursor_name}\n')
        stdout.write(f'heartbeat_at={daemon_runtime_state.heartbeat_at}\n')
        stdout.write(f'health_status={health.status}\n')
        stdout.write(f'health_score={health.score}\n')
        stdout.write(f'health_reason={health.reason}\n')
        return 0

    if args.command == 'poll-once':
        daemon_state.heartbeat()
        result = supervisor.poll_once()
        daemon_state.heartbeat()

        stdout.write(f'processed_events={result.processed_events}\n')
        stdout.write(f'next_offset={result.next_offset}\n')
        return 0

    parser.error(f'unsupported daemon command: {args.command}')
    return 2
