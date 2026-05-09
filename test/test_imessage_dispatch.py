from pathlib import Path

from room.imessage_correlation import IMessageCorrelationStore
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


def test_bind_imessage_source_event(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')
    correlation_store = IMessageCorrelationStore(
        project_root=tmp_path,
        store=store,
    )

    event = make_imessage_event()

    binding = correlation_store.bind_source_event(
        event,
        correlation_id='job_123',
    )

    assert binding is not None
    assert binding.recipient == '+886912345678'

    loaded = correlation_store.load_binding('job_123')

    assert loaded is not None
    assert loaded.chat_id == 'chat-1'


def test_dispatch_event_creates_correlation_binding(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    event = make_imessage_event()
    store.append(event)

    result = bridge.dispatch_event(event)

    assert result.correlation_binding is not None
    assert result.dispatch_result.submitted_event.type is RoomEventType.TASK_SUBMITTED


def test_create_agent_reply_uses_correlation_binding(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    source_event = make_imessage_event()
    store.append(source_event)

    dispatch_result = bridge.dispatch_event(source_event)

    correlation_id = (
        dispatch_result.dispatch_result.submitted_event.correlation_id
    )

    reply = bridge.create_agent_reply(
        correlation_id=correlation_id,
        agent_name='codex',
        body='tests fixed successfully',
    )

    assert reply.transport['recipient'] == '+886912345678'
    assert reply.transport['chat_id'] == 'chat-1'
    assert reply.metadata['has_correlation_binding'] is True
