from pathlib import Path

from cli.room import (
    format_room_event,
    list_room_events,
    render_room_events,
    send_room_message,
)


def test_send_room_message(tmp_path: Path):
    event = send_room_message(
        '@codex fix failing tests',
        project_root=tmp_path,
    )

    assert event.target == 'codex'
    assert event.body == 'fix failing tests'

    events = list_room_events(project_root=tmp_path)

    assert len(events) == 1
    assert events[0].body == 'fix failing tests'


def test_send_status_message(tmp_path: Path):
    event = send_room_message(
        '@status',
        project_root=tmp_path,
    )

    assert event.target == 'system'
    assert event.metadata['is_status'] is True


def test_render_room_events(tmp_path: Path):
    send_room_message(
        '@claude review latest diff',
        project_root=tmp_path,
    )

    send_room_message(
        '@gemini research latest api behavior',
        project_root=tmp_path,
    )

    output = render_room_events(
        list_room_events(project_root=tmp_path)
    )

    assert 'claude' in output
    assert 'gemini' in output
