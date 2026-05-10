from pathlib import Path

from room.dispatcher import RoomDispatchRequest
from room.models import RoomEventType
from room.store import RoomEventStore
from room.stream_executor import RoomAskStreamExecutor

from my_test.helpers.fake_process import FakePopen



def make_request() -> RoomDispatchRequest:
    return RoomDispatchRequest(
        target='codex',
        body='fix failing tests',
        source_event_id='evt_123',
        room_id='default',
        sender='you',
        source='cli',
    )


def test_each_stdout_line_becomes_agent_message(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=[
                'Analyzing issue\n',
                'Applying patch\n',
                'Tests passing\n',
            ],
            returncode=0,
        ),
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert len(result.output_events) == 3

    events = store.list_events()

    assert events[0].type is RoomEventType.AGENT_MESSAGE
    assert events[1].body == 'Applying patch'
    assert events[-1].type is RoomEventType.TASK_COMPLETED


def test_blank_stdout_lines_are_ignored(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=[
                '\n',
                'Useful output\n',
                '   \n',
            ],
            returncode=0,
        ),
    )

    result = rd.execute(make_request())

    assert len(result.output_events) == 1
    assert result.output_events[0].body == 'Useful output'


def test_failed_stream_produces_task_failed(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=['Provider crashed\\n'],
            returncode=1,
        ),
    )

    result = rd.execute(make_request())

    assert result.returncode == 1
    assert result.terminal_event is not None
    assert result.terminal_event.type is RoomEventType.TASK_FAILED


def test_on_event_callback_receives_all_events(tmp_path: Path):
    store = RoomEventStore(tmp_path / '.ccb' / 'room')

    emitted = []

    rd = RoomAskStreamExecutor(
        project_root=tmp_path,
        store=store,
        popen_fn=FakePopen(
            lines=[
                'step one\n',
                'step two\n',
            ],
            returncode=0,
        ),
        on_event=emitted.append,
    )

    result = rd.execute(make_request())

    assert result.returncode == 0
    assert len(emitted) == 3

    assert emitted[0].body == 'step one'
    assert emitted[1].body == 'step two'
    assert emitted[-1].type is RoomEventType.TASK_COMPLETED
