from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedStartCommand:
    project: Optional[str]
    agent_names: tuple[str, ...]
    restore: bool
    auto_permission: bool
    reset_context: bool = False
    kind: str = 'start'


@dataclass(frozen=True)
class ParsedKillCommand:
    project: Optional[str]
    force: bool = False
    kind: str = 'kill'


@dataclass(frozen=True)
class ParsedPsCommand:
    project: Optional[str]
    alive_only: bool = False
    kind: str = 'ps'


@dataclass(frozen=True)
class ParsedConfigValidateCommand:
    project: Optional[str]
    kind: str = 'config-validate'


@dataclass(frozen=True)
class ParsedDoctorCommand:
    project: Optional[str]
    bundle: bool = False
    output_path: Optional[str] = None
    kind: str = 'doctor'


@dataclass(frozen=True)
class ParsedLogsCommand:
    project: Optional[str]
    agent_name: str
    kind: str = 'logs'


@dataclass(frozen=True)
class ParsedPingCommand:
    project: Optional[str]
    target: str
    kind: str = 'ping'


__all__ = [
    'ParsedConfigValidateCommand',
    'ParsedDoctorCommand',
    'ParsedKillCommand',
    'ParsedLogsCommand',
    'ParsedPingCommand',
    'ParsedPsCommand',
    'ParsedStartCommand',
]
