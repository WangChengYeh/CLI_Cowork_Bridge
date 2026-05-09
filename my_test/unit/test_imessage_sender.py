from imessage.applescript import escape_applescript_string
from imessage.sender import (
    IMessageSendError,
    split_imessage_chunks,
)



def test_escape_applescript_string_handles_quotes():
    escaped = escape_applescript_string('hello "world"')

    assert '\\"' in escaped


def test_escape_applescript_string_handles_backslashes():
    escaped = escape_applescript_string('C:\\\\Users\\\\test')

    assert '\\\\\\\\' in escaped


def test_split_imessage_chunks_splits_long_messages():
    chunks = split_imessage_chunks('a' * 9000, chunk_size=3000)

    assert len(chunks) == 3
    assert all(len(chunk) <= 3000 for chunk in chunks)


def test_split_imessage_chunks_preserves_short_messages():
    chunks = split_imessage_chunks('hello world', chunk_size=3000)

    assert chunks == ['hello world']


def test_split_imessage_chunks_rejects_empty_limit():
    try:
        split_imessage_chunks('hello', chunk_size=0)
    except IMessageSendError:
        pass
    else:
        raise AssertionError('expected IMessageSendError')
