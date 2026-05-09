from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from ccbd.api_models import DeliveryScope, MessageEnvelope, TargetKind


@dataclass(frozen=True)
class _JobDraft:
    agent_name: str
    provider: str
    request: MessageEnvelope
    target_kind: TargetKind
    target_name: str
    provider_instance: Optional[str] = None
    provider_options: Optional[dict[str, object]] = None
    workspace_path: Optional[str] = None


@dataclass(frozen=True)
class _SubmissionPlan:
    project_id: str
    from_actor: str
    request: MessageEnvelope
    task_id: Optional[str]
    drafts: tuple[_JobDraft, ...]
    submission_id: Optional[str] = None
    target_scope: Optional[str] = None
    origin_message_id: Optional[str] = None


def _message_for_agent(request: MessageEnvelope, *, agent_name: str) -> MessageEnvelope:
    return MessageEnvelope(
        project_id=request.project_id,
        to_agent=agent_name,
        from_actor=request.from_actor,
        body=request.body,
        task_id=request.task_id,
        reply_to=request.reply_to,
        message_type=request.message_type,
        delivery_scope=DeliveryScope.SINGLE,
        silence_on_success=request.silence_on_success,
    )


__all__ = ['_JobDraft', '_message_for_agent', '_SubmissionPlan']
