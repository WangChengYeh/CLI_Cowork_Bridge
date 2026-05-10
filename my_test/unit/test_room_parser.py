from room.parser import RoomCommandError, parse_room_command


PARTICIPANTS = {'pm', 'rd', 'ae', 'it', 'test_agent'}


def test_parse_pm_command():
    parsed = parse_room_command(
        '@pm fix failing tests',
        participants=PARTICIPANTS,
    )

    assert parsed.target == 'pm'
    assert parsed.body == 'fix failing tests'
    assert parsed.command == 'message'


def test_parse_broadcast_command():
    parsed = parse_room_command(
        '@all rebuild project',
        participants=PARTICIPANTS,
    )

    assert parsed.target == 'all'
    assert parsed.body == 'rebuild project'
    assert parsed.command == 'broadcast'
    assert parsed.is_broadcast is True


def test_parse_status_command():
    parsed = parse_room_command(
        '@status',
        participants=PARTICIPANTS,
    )

    assert parsed.is_status is True
    assert parsed.target == 'status'


def test_custom_aliases_still_work():
    # Verify that passing custom aliases to the function still works
    aliases = {'code': 'rd'}
    assert parse_room_command('@code fix', participants=PARTICIPANTS, aliases=aliases).target == 'rd'


def test_unknown_participant_raises():
    try:
        parse_room_command('@unknown do work', participants=PARTICIPANTS)
    except RoomCommandError as exc:
        assert 'unknown participant: unknown' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')


def test_missing_prefix_raises():
    try:
        parse_room_command('pm fix tests', participants=PARTICIPANTS)
    except RoomCommandError as exc:
        assert 'command must start with @' in str(exc)
    else:
        raise AssertionError('expected RoomCommandError')
