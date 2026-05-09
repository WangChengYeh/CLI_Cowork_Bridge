from io import StringIO
from pathlib import Path

from cli.imessage_cli import run_imessage_cli



def test_imessage_doctor_prints_platform_fields(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_imessage_cli(
        ['doctor'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    output = stdout.getvalue()

    assert result == 0
    assert 'platform=' in output
    assert 'osascript_available=' in output


def test_imessage_send_dry_run_executes_without_failure(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_imessage_cli(
        [
            'send',
            '--recipient',
            '+886912345678',
            '--message',
            'hello world',
            '--dry-run',
        ],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0


def test_imessage_watch_dry_run_executes_poll_once(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_imessage_cli(
        ['watch', '--dry-run'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
