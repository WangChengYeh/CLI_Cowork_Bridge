from __future__ import annotations

from typing import Optional, Union

import time
from pathlib import Path

from provider_core.contracts import ProviderSessionBinding
from provider_core.session_binding_evidence import (
    AgentBinding,
    binding_status,
    default_binding_adapter,
    resolve_agent_binding as _resolve_agent_binding,
)


def _binding_adapter(provider: str) -> Optional[ProviderSessionBinding]:
    return default_binding_adapter(provider)


def resolve_agent_binding(
    *,
    provider: str,
    agent_name: str,
    workspace_path: Union[str, Path],
    project_root: Union[str, Optional[Path]] = None,
    ensure_usable: bool = False,
) -> Optional[AgentBinding]:
    return _resolve_agent_binding(
        provider=provider,
        agent_name=agent_name,
        workspace_path=workspace_path,
        project_root=project_root,
        ensure_usable=ensure_usable,
        adapter_resolver=_binding_adapter,
        sleep_fn=time.sleep,
    )


__all__ = ['AgentBinding', 'binding_status', 'resolve_agent_binding']
