from __future__ import annotations

from typing import Optional

from ccbd.models import CcbdShutdownReport, CcbdStartupReport
from storage.json_store import JsonStore
from storage.paths import PathLayout


class CcbdStartupReportStore:
    def __init__(self, layout: PathLayout, store: Optional[JsonStore] = None) -> None:
        self._layout = layout
        self._store = store or JsonStore()

    def load(self) -> Optional[CcbdStartupReport]:
        path = self._layout.ccbd_startup_report_path
        if not path.exists():
            return None
        return self._store.load(path, loader=CcbdStartupReport.from_record)

    def save(self, report: CcbdStartupReport) -> None:
        self._store.save(self._layout.ccbd_startup_report_path, report, serializer=lambda value: value.to_record())


class CcbdShutdownReportStore:
    def __init__(self, layout: PathLayout, store: Optional[JsonStore] = None) -> None:
        self._layout = layout
        self._store = store or JsonStore()

    def load(self) -> Optional[CcbdShutdownReport]:
        path = self._layout.ccbd_shutdown_report_path
        if not path.exists():
            return None
        return self._store.load(path, loader=CcbdShutdownReport.from_record)

    def save(self, report: CcbdShutdownReport) -> None:
        self._store.save(self._layout.ccbd_shutdown_report_path, report, serializer=lambda value: value.to_record())


__all__ = ['CcbdShutdownReportStore', 'CcbdStartupReportStore']
