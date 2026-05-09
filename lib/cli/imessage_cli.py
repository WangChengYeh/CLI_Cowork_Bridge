from __future__ import annotations

import argparse
from pathlib import Path
from typing import TextIO

from imessage.doctor import run_imessage_doctor
from imessage.sender import send_imessage
from imessage.watcher import IMessageWatcher


def build_imessage_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='ccb imessage')
    subparsers = parser.add_subparsers(dest='command', required=True)

    send_parser = subparsers.add_parser('send')
    send_parser.add_argument('--to', required=True)
    send_parser.add_argument('--message', required=True)
    send_parser.add_argument('--dry-run', action='store_true')

    doctor_parser = subparsers.add_parser('doctor')
    doctor_parser.add_argument('--json', action='store_true')

    watch_parser = subparsers.add_parser('watch')
    watch_parser.add_argument('--dry-run', action='store_true')
    watch_parser.add_argument('--once', action='store_true')

    return parser


def run_imessage_cli(
    argv: list[str],
    *,
    project_root: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    del stderr
    parser = build_imessage_parser()
    args = parser.parse_args(argv)

    if args.command == 'send':
        results = send_imessage(
            recipient=args.to,
            message=args.message,
            dry_run=args.dry_run,
        )
        stdout.write(f'sent {len(results)} message chunk(s)\n')
        return 0

    if args.command == 'doctor':
        result = run_imessage_doctor()
        stdout.write(f'platform_supported={result.platform_supported}\n')
        stdout.write(f'osascript_available={result.osascript_available}\n')
        stdout.write(f'messages_db_exists={result.messages_db_exists}\n')
        for note in result.notes:
            stdout.write(f'- {note}\n')
        return 0

    if args.command == 'watch':
        watcher = IMessageWatcher(project_root=project_root)
        decisions = watcher.poll_once(dry_run=args.dry_run)
        stdout.write(f'processed {len(decisions)} message(s)\n')
        return 0

    parser.error(f'unsupported imessage command: {args.command}')
    return 2
