from pathlib import Path

from room.imessage_dispatch import IMessageDispatchBridge
from room.models import RoomEvent, RoomEventType, RoomSource
from room.store import RoomEventStore


def make_imessage_event() -> RoomEvent:
    return RoomEvent(
        room_id='default',
        source=RoomSource.IMESSAGE,
        sender='you',
        target='codex',
        type=RoomEventType.USER_MESSAGE,
        body='fix failing tests',
        transport={
            'name': 'imessage',
            'chat_id': 'chat-1',
            'message_id': 123,
            'sender_handle': '+886912345678',
        },
    )


def test_dispatch_event_creates_task_submitted(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    event = make_imessage_event()
    store.append(event)

    result = bridge.dispatch_event(event)

    assert result.dispatch_result.submitted_event.type is RoomEventType.TASK_SUBMITTED
    assert result.correlation_binding is not None


def test_create_agent_reply_restores_transport_metadata(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    event = make_imessage_event()
    store.append(event)

    result = bridge.dispatch_event(event)

    correlation_id = result.dispatch_result.submitted_event.correlation_id

    reply = bridge.create_agent_reply(
        correlation_id=correlation_id,
        agent_name='codex',
        body='tests fixed successfully',
    )

    assert reply.transport['recipient'] == '+886912345678'
    assert reply.transport['chat_id'] == 'chat-1'
    assert reply.transport['message_id'] == 123


def test_missing_binding_still_creates_reply(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    reply = bridge.create_agent_reply(
        correlation_id='missing-binding',
        agent_name='codex',
        body='fallback reply',
    )

    assert reply.type is RoomEventType.AGENT_MESSAGE
    assert reply.transport['recipient'] is None
    assert reply.metadata['has_correlation_binding'] is False
