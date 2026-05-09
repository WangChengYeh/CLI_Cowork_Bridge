from __future__ import annotations

import argparse
from pathlib import Path
from typing import TextIO

from runtime.supervisor import RuntimeSupervisor


STATE_STOPPED = 'stopped'
STATE_RUNNING = 'running'


def build_daemon_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='ccb daemon')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('start')
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

    supervisor = RuntimeSupervisor(project_root=project_root)

    if args.command == 'start':
        stdout.write(f'{STATE_RUNNING}\n')
        return 0

    if args.command == 'stop':
        stdout.write(f'{STATE_STOPPED}\n')
        return 0

    if args.command == 'status':
        status = supervisor.status()
        stdout.write(f'worker_count={status.worker_count}\n')
        stdout.write(f'cursor_name={status.cursor_name}\n')
        return 0

    if args.command == 'poll-once':
        result = supervisor.poll_once()
        stdout.write(f'processed_events={result.processed_events}\n')
        stdout.write(f'next_offset={result.next_offset}\n')
        return 0

    parser.error(f'unsupported daemon command: {args.command}')
    return 2
