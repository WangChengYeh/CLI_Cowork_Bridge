from io import StringIO
from pathlib import Path

from cli.room_cli import run_room_cli



def test_room_send_appends_event_and_prints_id(tmp_path: Path):
    stdout = StringIO()
    stderr = StringIO()

    result = run_room_cli(
        ['send', '@codex fix failing tests'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert stdout.getvalue().startswith('evt_')


def test_room_events_renders_stored_events(tmp_path: Path):
    run_room_cli(
        ['send', '@claude review diff'],
        project_root=tmp_path,
        stdout=StringIO(),
        stderr=StringIO(),
    )

    stdout = StringIO()
    stderr = StringIO()

    result = run_room_cli(
        ['events'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert 'claude' in stdout.getvalue()
    assert 'review diff' in stdout.getvalue()


def test_room_status_uses_event_renderer(tmp_path: Path):
    run_room_cli(
        ['send', '@gemini research api'],
        project_root=tmp_path,
        stdout=StringIO(),
        stderr=StringIO(),
    )

    stdout = StringIO()
    stderr = StringIO()

    result = run_room_cli(
        ['status'],
        project_root=tmp_path,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert 'gemini' in stdout.getvalue()
