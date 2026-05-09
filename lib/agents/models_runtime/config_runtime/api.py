from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class AgentApiSpec:
    key: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'key', _normalize_text(self.key))
        object.__setattr__(self, 'url', _normalize_text(self.url))

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {}
        if self.key is not None:
            record['key'] = self.key
        if self.url is not None:
            record['url'] = self.url
        return record


def _normalize_text(value: object) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


__all__ = ['AgentApiSpec']
