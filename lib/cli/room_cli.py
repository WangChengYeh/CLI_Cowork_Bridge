from __future__ import annotations

import argparse
from pathlib import Path
from typing import TextIO

from cli.room import list_room_events, render_room_events, send_room_message


def build_room_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='ccb room')
    subparsers = parser.add_subparsers(dest='command', required=True)

    send_parser = subparsers.add_parser('send')
    send_parser.add_argument('message')

    events_parser = subparsers.add_parser('events')
    events_parser.add_argument('--limit', type=int, default=20)

    status_parser = subparsers.add_parser('status')
    status_parser.add_argument('--limit', type=int, default=20)

    return parser


def run_room_cli(
    argv: list[str],
    *,
    project_root: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    del stderr
    parser = build_room_parser()
    args = parser.parse_args(argv)

    if args.command == 'send':
        event = send_room_message(
            args.message,
            project_root=project_root,
        )
        stdout.write(f'{event.event_id}\n')
        return 0

    if args.command in {'events', 'status'}:
        events = list_room_events(
            project_root=project_root,
            limit=args.limit,
        )
        output = render_room_events(events)
        if output:
            stdout.write(output + '\n')
        return 0

    parser.error(f'unsupported room command: {args.command}')
    return 2
