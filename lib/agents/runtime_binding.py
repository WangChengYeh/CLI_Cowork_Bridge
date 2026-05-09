from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


def _normalize(value: Optional[str]) -> Optional[str]:
    text = str(value or '').strip()
    return text or None


@dataclass(frozen=True)
class RuntimeBinding:
    runtime_ref: Optional[str]
    session_ref: Optional[str]
    workspace_path: Optional[str]

    @property
    def status(self) -> str:
        if self.runtime_ref and self.session_ref and self.workspace_path:
            return 'bound'
        if self.runtime_ref or self.session_ref or self.workspace_path:
            return 'partial'
        return 'unbound'

    @property
    def is_bound(self) -> bool:
        return self.status == 'bound'

    def to_fields(self) -> dict[str, Optional[str]]:
        return {
            'runtime_ref': self.runtime_ref,
            'session_ref': self.session_ref,
            'workspace_path': self.workspace_path,
            'binding_status': self.status,
        }


def build_runtime_binding(
    *,
    runtime_ref: Optional[str] = None,
    session_ref: Optional[str] = None,
    workspace_path: Optional[str] = None,
) -> RuntimeBinding:
    return RuntimeBinding(
        runtime_ref=_normalize(runtime_ref),
        session_ref=_normalize(session_ref),
        workspace_path=_normalize(workspace_path),
    )


def merge_runtime_binding(
    existing: Optional[RuntimeBinding],
    *,
    runtime_ref: Optional[str] = None,
    session_ref: Optional[str] = None,
    workspace_path: Optional[str] = None,
) -> RuntimeBinding:
    current = existing or build_runtime_binding()
    return build_runtime_binding(
        runtime_ref=runtime_ref if runtime_ref is not None else current.runtime_ref,
        session_ref=session_ref if session_ref is not None else current.session_ref,
        workspace_path=workspace_path if workspace_path is not None else current.workspace_path,
    )


def runtime_binding_from_runtime(runtime) -> RuntimeBinding:
    if runtime is None:
        return build_runtime_binding()
    return build_runtime_binding(
        runtime_ref=getattr(runtime, 'runtime_ref', None),
        session_ref=getattr(runtime, 'session_ref', None),
        workspace_path=getattr(runtime, 'workspace_path', None),
    )
