from lib.room.parser import RoomCommandError, parse_room_command


PARTICIPANTS = {'codex', 'claude', 'gemini', 'pm', 'rd', 'ae'}


def test_parse_codex_message():
    result = parse_room_command(
        '@codex fix failing tests',
        participants=PARTICIPANTS,
    )

    assert result.command == 'message'
    assert result.target == 'rd'
    assert result.body == 'fix failing tests'


def test_parse_alias_claude_to_pm():
    result = parse_room_command(
        '@claude summarize',
        participants=PARTICIPANTS,
    )
    assert result.target == 'pm'


def test_parse_alias_gemini_to_ae():
    result = parse_room_command(
        '@gemini audit',
        participants=PARTICIPANTS,
    )
    assert result.target == 'ae'


def test_parse_alias_review():
    result = parse_room_command(
        '@review check latest diff',
        participants=PARTICIPANTS,
    )

    assert result.target == 'ae'


def test_parse_status_command():
    result = parse_room_command(
        '@status',
        participants=PARTICIPANTS,
    )

    assert result.is_status is True


def test_parse_broadcast_command():
    result = parse_room_command(
        '@all sync current status',
        participants=PARTICIPANTS,
    )

    assert result.is_broadcast is True
    assert result.body == 'sync current status'


def test_reject_unknown_target():
    try:
        parse_room_command(
            '@unknown hello',
            participants=PARTICIPANTS,
        )
    except RoomCommandError as exc:
        assert 'unknown participant' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')


def test_reject_missing_body():
    try:
        parse_room_command(
            '@codex',
            participants=PARTICIPANTS,
        )
    except RoomCommandError as exc:
        assert 'message body cannot be empty' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')
