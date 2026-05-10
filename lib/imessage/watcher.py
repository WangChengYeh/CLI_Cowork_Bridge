from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from room.models import RoomEvent, RoomEventType, RoomSource
from room.parser import RoomCommandError, parse_room_command
from room.store import RoomEventStore


class IMessageWatchError(RuntimeError):
    pass


@dataclass
class IMessageInboundMessage:
    message_id: int
    chat_id: Optional[str]
    sender_handle: str
    text: str
    is_from_me: bool


@dataclass
class IMessageWatchDecision:
    message: IMessageInboundMessage
    accepted: bool
    reason: Optional[str] = None
    event: Optional[RoomEvent] = None


DEFAULT_PARTICIPANTS = {'codex', 'claude', 'gemini'}


def default_messages_db_path() -> Path:
    return Path.home() / 'Library' / 'Messages' / 'chat.db'


def read_inbound_messages(
    db_path: Path,
    *,
    after_message_id: int = 0,
    limit: int = 50,
) -> list[IMessageInboundMessage]:
    if limit <= 0:
        raise IMessageWatchError('limit must be positive')

    if not db_path.exists():
        raise IMessageWatchError(f'Messages database not found: {db_path}')

    query = '''
        SELECT
            message.ROWID,
            chat.chat_identifier,
            handle.id,
            message.text,
            message.is_from_me
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.ROWID
        LEFT JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
        LEFT JOIN chat ON chat_message_join.chat_id = chat.ROWID
        WHERE message.ROWID > ?
        ORDER BY message.ROWID ASC
        LIMIT ?
    '''

    messages: list[IMessageInboundMessage] = []

    connection = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    try:
        for row in connection.execute(query, (after_message_id, limit)):
            message_id, chat_id, sender_handle, text, is_from_me = row
            messages.append(
                IMessageInboundMessage(
                    message_id=int(message_id),
                    chat_id=str(chat_id) if chat_id is not None else None,
                    sender_handle=str(sender_handle or ''),
                    text=str(text or ''),
                    is_from_me=bool(is_from_me),
                )
            )
    finally:
        connection.close()

    return messages


class IMessageWatcher:
    def __init__(
        self,
        *,
        project_root: Path,
        db_path: Optional[Path] = None,
        allow_senders: Optional[set[str]] = None,
        prefix: str = '@',
        participants: Optional[set[str]] = None,
        store: Optional[RoomEventStore] = None,
    ) -> None:
        self.project_root = project_root
        self.db_path = db_path or default_messages_db_path()
        self.allow_senders = allow_senders or set()
        self.prefix = prefix
        self.participants = participants or DEFAULT_PARTICIPANTS
        self.store = store or RoomEventStore(project_root / '.ccb' / 'room')

    def read_cursor(self) -> int:
        return self.store.read_cursor('imessage')

    def write_cursor(self, message_id: int) -> None:
        self.store.write_cursor('imessage', message_id)

    def poll_once(self, *, limit: int = 500, dry_run: bool = False) -> list[IMessageWatchDecision]:
        after_message_id = self.read_cursor()
        messages = read_inbound_messages(
            self.db_path,
            after_message_id=after_message_id,
            limit=limit,
        )

        decisions = [self.evaluate_message(message, dry_run=dry_run) for message in messages]

        if messages:
            self.write_cursor(max(message.message_id for message in messages))

        return decisions

    def evaluate_message(self, message: IMessageInboundMessage, *, dry_run: bool = False) -> IMessageWatchDecision:
        if message.is_from_me:
            return self._reject(message, 'outgoing message ignored')

        if not message.text.strip():
            return self._reject(message, 'empty message ignored')

        if self.allow_senders and message.sender_handle not in self.allow_senders:
            return self._reject(message, 'sender not allowlisted')

        if not message.text.strip().startswith(self.prefix):
            return self._reject(message, 'prefix not matched')

        try:
            parsed = parse_room_command(
                message.text,
                participants=self.participants,
                prefix=self.prefix,
            )
        except RoomCommandError as exc:
            return self._reject(message, str(exc))

        if parsed.is_status:
            event_type = RoomEventType.STATUS_SNAPSHOT
            target = 'system'
            body = 'status requested'
        else:
            event_type = RoomEventType.USER_MESSAGE
            target = parsed.target
            body = parsed.body

        event = RoomEvent(
            room_id='default',
            source=RoomSource.IMESSAGE,
            sender='you',
            target=target,
            type=event_type,
            body=body,
            transport={
                'name': 'imessage',
                'chat_id': message.chat_id,
                'message_id': message.message_id,
                'sender_handle': message.sender_handle,
            },
            metadata={
                'raw_text': parsed.raw_text,
                'command': parsed.command,
                'is_broadcast': parsed.is_broadcast,
                'is_status': parsed.is_status,
            },
        )

        if not dry_run:
            self.store.append(event)

        return IMessageWatchDecision(message=message, accepted=True, event=event)

    def _reject(self, message: IMessageInboundMessage, reason: str) -> IMessageWatchDecision:
        self.store.append_audit(
            {
                'type': 'imessage_rejected',
                'message_id': message.message_id,
                'sender_handle': message.sender_handle,
                'reason': reason,
            }
        )
        return IMessageWatchDecision(message=message, accepted=False, reason=reason)
