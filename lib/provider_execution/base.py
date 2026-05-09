from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol

from ccbd.api_models import JobRecord
from completion.models import (
    CompletionConfidence,
    CompletionDecision,
    CompletionItem,
    CompletionSourceKind,
    CompletionStatus,
)


@dataclass(frozen=True)
class ProviderRuntimeContext:
    agent_name: str
    workspace_path: Optional[str]
    backend_type: Optional[str]
    runtime_ref: Optional[str]
    session_ref: Optional[str]
    runtime_pid: Optional[int] = None
    runtime_health: Optional[str] = None
    runtime_binding_source: Optional[str] = None


@dataclass(frozen=True)
class ProviderSubmission:
    job_id: str
    agent_name: str
    provider: str
    accepted_at: str
    ready_at: str
    source_kind: CompletionSourceKind
    reply: str
    status: CompletionStatus = CompletionStatus.INCOMPLETE
    reason: str = 'in_progress'
    confidence: CompletionConfidence = CompletionConfidence.OBSERVED
    diagnostics: Optional[dict] = None
    runtime_state: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderPollResult:
    submission: ProviderSubmission
    items: tuple[CompletionItem, ...] = ()
    decision: Optional[CompletionDecision] = None

    def __post_init__(self) -> None:
        if self.decision is not None and not self.decision.terminal:
            raise ValueError('provider poll decisions must be terminal')


class ProviderExecutionAdapter(Protocol):
    provider: str

    def start(self, job: JobRecord, *, context: Optional[ProviderRuntimeContext], now: str) -> ProviderSubmission:
        ...

    def poll(self, submission: ProviderSubmission, *, now: str) -> Optional[ProviderPollResult]:
        ...
