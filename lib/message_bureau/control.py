from __future__ import annotations

from typing import Optional

from datetime import datetime, timezone

from jobs.store import JobStore, SubmissionStore
from mailbox_runtime.targets import known_mailbox_targets
from mailbox_kernel import (
    DeliveryLeaseStore,
    InboundEventStore,
    MailboxKernelService,
    MailboxStore,
)
from storage.paths import PathLayout

from .control_queue import ack_reply as control_ack_reply
from .control_queue import agent_queue as control_agent_queue
from .control_queue import inbox as control_inbox
from .control_queue import queue_summary as control_queue_summary
from .control_trace import trace as control_trace
from .service_state import MessageBureauControlRuntimeState, MessageBureauControlStateMixin
from .store import AttemptStore, MessageStore, ReplyStore


class MessageBureauControlService(MessageBureauControlStateMixin):
    def __init__(
        self,
        layout: PathLayout,
        config,
        *,
        mailbox_store: Optional[MailboxStore] = None,
        inbound_store: Optional[InboundEventStore] = None,
        lease_store: Optional[DeliveryLeaseStore] = None,
        message_store: Optional[MessageStore] = None,
        attempt_store: Optional[AttemptStore] = None,
        reply_store: Optional[ReplyStore] = None,
        job_store: Optional[JobStore] = None,
        submission_store: Optional[SubmissionStore] = None,
        mailbox_kernel: Optional[MailboxKernelService] = None,
        clock=None,
    ) -> None:
        resolved_clock = clock or _utc_now
        mailbox_store = mailbox_store or MailboxStore(layout)
        inbound_store = inbound_store or InboundEventStore(layout)
        lease_store = lease_store or DeliveryLeaseStore(layout)
        message_store = message_store or MessageStore(layout)
        attempt_store = attempt_store or AttemptStore(layout)
        reply_store = reply_store or ReplyStore(layout)
        self._runtime_state = MessageBureauControlRuntimeState(
            layout=layout,
            config=config,
            known_mailboxes=known_mailbox_targets(config),
            clock=resolved_clock,
            mailbox_store=mailbox_store,
            inbound_store=inbound_store,
            lease_store=lease_store,
            message_store=message_store,
            attempt_store=attempt_store,
            reply_store=reply_store,
            job_store=job_store or JobStore(layout),
            submission_store=submission_store or SubmissionStore(layout),
            mailbox_kernel=mailbox_kernel or MailboxKernelService(
                layout,
                clock=resolved_clock,
                mailbox_store=mailbox_store,
                inbound_store=inbound_store,
                lease_store=lease_store,
            ),
        )

    def queue_summary(self, target: str = 'all') -> dict[str, object]:
        return control_queue_summary(self, target)

    def agent_queue(self, agent_name: str) -> dict[str, object]:
        return control_agent_queue(self, agent_name)

    def trace(self, target: str) -> dict[str, object]:
        return control_trace(self, target)

    def inbox(self, agent_name: str) -> dict[str, object]:
        return control_inbox(self, agent_name)

    def ack_reply(self, agent_name: str, inbound_event_id: Optional[str] = None) -> dict[str, object]:
        return control_ack_reply(self, agent_name, inbound_event_id=inbound_event_id)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


__all__ = ['MessageBureauControlService']
