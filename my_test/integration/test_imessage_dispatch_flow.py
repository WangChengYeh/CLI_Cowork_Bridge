from pathlib import Path

from imessage.watcher import IMessageInboundMessage, IMessageWatcher
from room.imessage_dispatch import IMessageDispatchBridge
from room.models import RoomEventType
from room.store import RoomEventStore


PARTICIPANTS = {'codex', 'claude', 'gemini'}



def make_message() -> IMessageInboundMessage:
    return IMessageInboundMessage(
        message_id=123,
        chat_id='chat-1',
        sender_handle='+886912345678',
        text='@codex fix failing tests',
        is_from_me=False,
    )


def test_imessage_to_dispatch_flow_preserves_correlation(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    watcher = IMessageWatcher(
        project_root=tmp_path,
        allow_senders={'+886912345678'},
        participants=PARTICIPANTS,
        store=store,
    )

    decision = watcher.evaluate_message(make_message())

    assert decision.accepted is True
    assert decision.event is not None

    bridge = IMessageDispatchBridge(
        project_root=tmp_path,
        store=store,
    )

    dispatch_result = bridge.dispatch_event(decision.event)

    submitted = dispatch_result.dispatch_result.submitted_event

    assert submitted.type is RoomEventType.TASK_SUBMITTED
    assert dispatch_result.correlation_binding is not None

    reply = bridge.create_agent_reply(
        correlation_id=submitted.correlation_id,
        agent_name='codex',
        body='tests fixed successfully',
    )

    assert reply.transport['recipient'] == '+886912345678'
    assert reply.transport['chat_id'] == 'chat-1'
    assert reply.transport['message_id'] == 123

    assert reply.metadata['has_correlation_binding'] is True
