from imessage.sender import (
    IMessageSendError,
    chunk_imessage_text,
    escape_applescript_string,
)



def test_escape_applescript_string_handles_quotes():
    escaped = escape_applescript_string('hello "world"')

    assert '\\"' in escaped


def test_escape_applescript_string_handles_backslashes():
    escaped = escape_applescript_string('C:\\\\Users\\\\test')

    assert '\\\\\\\\' in escaped


def test_chunk_imessage_text_splits_long_messages():
    chunks = chunk_imessage_text('a' * 9000, limit=3000)

    assert len(chunks) == 3
    assert all(len(chunk) <= 3000 for chunk in chunks)


def test_chunk_imessage_text_preserves_short_messages():
    chunks = chunk_imessage_text('hello world', limit=3000)

    assert chunks == ['hello world']


def test_chunk_imessage_text_rejects_empty_limit():
    try:
        chunk_imessage_text('hello', limit=0)
    except IMessageSendError:
        pass
    else:
        raise AssertionError('expected IMessageSendError')
