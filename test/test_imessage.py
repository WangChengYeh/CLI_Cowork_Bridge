from imessage.applescript import (
    build_send_imessage_script,
    escape_applescript_string,
)
from imessage.sender import split_imessage_chunks


def test_escape_applescript_string():
    value = 'hello "world"'

    escaped = escape_applescript_string(value)

    assert '\\"' in escaped


def test_build_send_script_contains_recipient_and_message():
    script = build_send_imessage_script(
        recipient='+886912345678',
        message='hello',
    )

    assert 'Messages' in script
    assert '+886912345678' in script
    assert 'hello' in script


def test_split_imessage_chunks():
    message = 'a' * 9000

    chunks = split_imessage_chunks(message, chunk_size=4000)

    assert len(chunks) == 3
    assert len(chunks[0]) == 4000
    assert len(chunks[1]) == 4000
    assert len(chunks[2]) == 1000
