from __future__ import annotations


def escape_applescript_string(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def build_send_imessage_script(*, recipient: str, message: str) -> str:
    escaped_recipient = escape_applescript_string(recipient)
    escaped_message = escape_applescript_string(message)

    return f'''tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{escaped_recipient}" of targetService
    send "{escaped_message}" to targetBuddy
end tell'''
