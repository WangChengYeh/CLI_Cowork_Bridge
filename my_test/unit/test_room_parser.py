from room.parser import RoomCommandError, parse_room_command


PARTICIPANTS = {'codex', 'claude', 'gemini', 'pm', 'rd', 'ae'}


def test_parse_codex_command():
    parsed = parse_room_command(
        '@codex fix failing tests',
        participants=PARTICIPANTS,
    )

    assert parsed.target == 'rd'
    assert parsed.body == 'fix failing tests'
    assert parsed.command == 'message'


def test_parse_broadcast_command():
    parsed = parse_room_command(
        '@all sync current status',
        participants=PARTICIPANTS,
    )

    assert parsed.target == 'all'
    assert parsed.is_broadcast is True
    assert parsed.body == 'sync current status'


def test_parse_status_command():
    parsed = parse_room_command(
        '@status',
        participants=PARTICIPANTS,
    )

    assert parsed.is_status is True
    assert parsed.target == 'status'


def test_aliases_are_normalized():
    assert parse_room_command('@code fix', participants=PARTICIPANTS).target == 'rd'
    assert parse_room_command('@review diff', participants=PARTICIPANTS).target == 'ae'
    assert parse_room_command('@research api', participants=PARTICIPANTS).target == 'ae'
    assert parse_room_command('@claude summarize', participants=PARTICIPANTS).target == 'pm'
    assert parse_room_command('@gemini audit', participants=PARTICIPANTS).target == 'ae'
    assert parse_room_command('@codex start', participants=PARTICIPANTS).target == 'rd'


def test_unknown_participant_raises():
    try:
        parse_room_command('@unknown do work', participants=PARTICIPANTS)
    except RoomCommandError as exc:
        assert 'unknown participant' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')


def test_missing_body_raises_for_normal_target():
    try:
        parse_room_command('@codex', participants=PARTICIPANTS)
    except RoomCommandError as exc:
        assert 'message body cannot be empty' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')


def test_missing_prefix_raises():
    try:
        parse_room_command('codex fix tests', participants=PARTICIPANTS)
    except RoomCommandError as exc:
        assert 'command must start' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')
