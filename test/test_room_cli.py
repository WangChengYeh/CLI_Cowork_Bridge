from io import StringIO
from pathlib import Path

from cli.room_cli import run_room_cli


def test_room_send_cli(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run_room_cli(
        ['send', '@codex fix tests'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert 'evt_' in stdout.getvalue()


def test_room_events_cli(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    run_room_cli(
        ['send', '@claude review diff'],
        project_root=tmp_path,
        stdout=StringIO(),
        stderr=StringIO(),
    )

    exit_code = run_room_cli(
        ['events'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert 'claude' in stdout.getvalue()
