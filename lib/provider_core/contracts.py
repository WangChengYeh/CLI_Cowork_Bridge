from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Optional, Union

from agents.models import AgentSpec
from cli.context import CliContext
from cli.models import ParsedStartCommand
from provider_execution.base import ProviderExecutionAdapter
from workspace.models import WorkspacePlan

from .manifests import ProviderManifest


@dataclass(frozen=True)
class ProviderRuntimeIdentity:
    state: str
    reason: Optional[str] = None


@dataclass(frozen=True)
class ProviderSessionBinding:
    provider: str
    load_session: Callable[[Path, Optional[str]], Optional[object]]
    session_id_attr: str
    session_path_attr: str
    live_runtime_identity: Optional[Callable[[object], Optional[ProviderRuntimeIdentity]]] = None

    def __post_init__(self) -> None:
        provider = str(self.provider or '').strip().lower()
        if not provider:
            raise ValueError('provider cannot be empty')
        object.__setattr__(self, 'provider', provider)


@dataclass(frozen=True)
class ProviderRuntimeLauncher:
    provider: str
    launch_mode: Literal['simple_tmux', 'codex_tmux']
    build_start_cmd: Callable[[ParsedStartCommand, AgentSpec, Path, str], str]
    build_session_payload: Callable[[CliContext, AgentSpec, WorkspacePlan, Path, Path, str, str, str, dict[str, object]], dict[str, object]]
    prepare_runtime: Optional[Callable[[Path], dict[str, Optional[object]]]] = None
    post_launch: Optional[Callable[[object, str, Path, str, dict[str, object]], None]] = None
    resolve_run_cwd: Optional[Callable[[ParsedStartCommand, AgentSpec, WorkspacePlan, Path, str], Union[Path, Optional[str]]]] = None

    def __post_init__(self) -> None:
        provider = str(self.provider or '').strip().lower()
        if not provider:
            raise ValueError('provider cannot be empty')
        object.__setattr__(self, 'provider', provider)


@dataclass(frozen=True)
class ProviderBackend:
    manifest: ProviderManifest
    execution_adapter: Optional[ProviderExecutionAdapter] = None
    session_binding: Optional[ProviderSessionBinding] = None
    runtime_launcher: Optional[ProviderRuntimeLauncher] = None

    @property
    def provider(self) -> str:
        return self.manifest.provider


__all__ = ['ProviderBackend', 'ProviderRuntimeIdentity', 'ProviderRuntimeLauncher', 'ProviderSessionBinding']
