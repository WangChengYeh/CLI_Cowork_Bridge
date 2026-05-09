from __future__ import annotations

import argparse
from pathlib import Path
from typing import TextIO

from runtime.bootstrap import bootstrap_runtime
from runtime.daemon_runner import run_runtime_forever
from runtime.daemon_state import RuntimeDaemonStateStore


STATE_STOPPED = 'stopped'
STATE_RUNNING = 'running'


DEFAULT_FOREGROUND_ITERATIONS = 1


def build_daemon_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='ccb daemon')
    subparsers = parser.add_subparsers(dest='command', required=True)

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument(
        '--foreground',
        action='store_true',
    )

    subparsers.add_parser('stop')
    subparsers.add_parser('status')
    subparsers.add_parser('poll-once')

    return parser


def run_daemon_cli(
    argv: list[str],
    *,
    project_root: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    del stderr

    parser = build_daemon_parser()
    args = parser.parse_args(argv)

    runtime = bootstrap_runtime(project_root=project_root)
    supervisor = runtime.supervisor

    daemon_state = RuntimeDaemonStateStore(
        project_root=project_root,
    )

    if args.command == 'start':
        state = daemon_state.mark_running()
        stdout.write(f'{state.state}\n')
        stdout.write(f'pid={state.pid}\n')

        if args.foreground:
            result = run_runtime_forever(
                project_root=project_root,
                bootstrap=runtime,
                max_iterations=DEFAULT_FOREGROUND_ITERATIONS,
            )

            stdout.write(
                f'foreground_iterations={result.iterations}\n'
            )
            stdout.write(
                f'foreground_processed_events={result.processed_events}\n'
            )

        return 0

    if args.command == 'stop':
        state = daemon_state.mark_stopped()
        stdout.write(f'{state.state}\n')
        return 0

    if args.command == 'status':
        runtime_status = supervisor.status()
        daemon_runtime_state = daemon_state.read()

        stdout.write(f'state={daemon_runtime_state.state}\n')
        stdout.write(f'pid={daemon_runtime_state.pid}\n')
        stdout.write(f'worker_count={runtime_status.worker_count}\n')
        stdout.write(f'cursor_name={runtime_status.cursor_name}\n')
        stdout.write(
            f'heartbeat_at={daemon_runtime_state.heartbeat_at}\n'
        )
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
