from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedAskCommand:
    project: Optional[str]
    target: str
    sender: Optional[str]
    message: str
    task_id: Optional[str] = None
    reply_to: Optional[str] = None
    mode: Optional[str] = None
    silence: bool = False
    wait: bool = False
    output_path: Optional[str] = None
    timeout_s: Optional[float] = None
    kind: str = 'ask'


@dataclass(frozen=True)
class ParsedAskWaitCommand:
    project: Optional[str]
    job_id: str
    timeout_s: Optional[float] = None
    kind: str = 'ask-wait'


@dataclass(frozen=True)
class ParsedCancelCommand:
    project: Optional[str]
    job_id: str
    kind: str = 'cancel'


@dataclass(frozen=True)
class ParsedPendCommand:
    project: Optional[str]
    target: str
    count: Optional[int] = None
    kind: str = 'pend'


@dataclass(frozen=True)
class ParsedQueueCommand:
    project: Optional[str]
    target: str
    kind: str = 'queue'


@dataclass(frozen=True)
class ParsedTraceCommand:
    project: Optional[str]
    target: str
    kind: str = 'trace'


@dataclass(frozen=True)
class ParsedResubmitCommand:
    project: Optional[str]
    message_id: str
    kind: str = 'resubmit'


@dataclass(frozen=True)
class ParsedRetryCommand:
    project: Optional[str]
    target: str
    kind: str = 'retry'


@dataclass(frozen=True)
class ParsedWaitCommand:
    project: Optional[str]
    mode: str
    target: str
    quorum: Optional[int] = None
    timeout_s: Optional[float] = None
    kind: str = 'wait'


@dataclass(frozen=True)
class ParsedWatchCommand:
    project: Optional[str]
    target: str
    kind: str = 'watch'


@dataclass(frozen=True)
class ParsedInboxCommand:
    project: Optional[str]
    agent_name: str
    kind: str = 'inbox'


@dataclass(frozen=True)
class ParsedAckCommand:
    project: Optional[str]
    agent_name: str
    inbound_event_id: Optional[str] = None
    kind: str = 'ack'


__all__ = [
    'ParsedAckCommand',
    'ParsedAskCommand',
    'ParsedAskWaitCommand',
    'ParsedCancelCommand',
    'ParsedInboxCommand',
    'ParsedPendCommand',
    'ParsedQueueCommand',
    'ParsedResubmitCommand',
    'ParsedRetryCommand',
    'ParsedTraceCommand',
    'ParsedWaitCommand',
    'ParsedWatchCommand',
]
