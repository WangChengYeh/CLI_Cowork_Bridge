from imessage.doctor import run_imessage_doctor



def test_non_darwin_platform_reports_unsupported():
    result = run_imessage_doctor(
        platform_name='Linux',
        osascript_available=False,
        chat_db_exists=False,
    )

    assert result.platform_supported is False
    assert result.ok is False


def test_missing_osascript_reports_unavailable():
    result = run_imessage_doctor(
        platform_name='Darwin',
        osascript_available=False,
        chat_db_exists=True,
    )

    assert result.platform_supported is True
    assert result.osascript_available is False
    assert result.ok is False


def test_missing_chat_db_adds_note():
    result = run_imessage_doctor(
        platform_name='Darwin',
        osascript_available=True,
        chat_db_exists=False,
    )

    assert any('chat.db' in note for note in result.notes)


def test_ok_requires_platform_and_osascript():
    result = run_imessage_doctor(
        platform_name='Darwin',
        osascript_available=True,
        chat_db_exists=True,
    )

    assert result.ok is True


def test_full_disk_access_note_is_present():
    result = run_imessage_doctor(
        platform_name='Darwin',
        osascript_available=True,
        chat_db_exists=True,
    )

    assert any('Full Disk Access' in note for note in result.notes)
