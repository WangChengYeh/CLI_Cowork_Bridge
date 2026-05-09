from __future__ import annotations

from typing import Optional

import os
import sys
import subprocess
from pathlib import Path

from .utils import coerce_pid


def read_pid_file(path: Path) -> Optional[int]:
    try:
        return coerce_pid(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def read_proc_path(pid: int, entry: str) -> Optional[Path]:
    if sys.platform == 'darwin':
        if entry == 'cwd':
            try:
                # -p pid, -a AND, -d cwd, -F n (field name: n for file name)
                output = subprocess.check_output(
                    ['lsof', '-p', str(pid), '-a', '-d', 'cwd', '-Fn'],
                    encoding='utf-8',
                    stderr=subprocess.DEVNULL,
                )
                for line in output.splitlines():
                    if line.startswith('n'):
                        return Path(line[1:]).expanduser()
            except Exception:
                pass
        return None

    try:
        return Path(os.readlink(f'/proc/{pid}/{entry}')).expanduser()
    except Exception:
        return None


def read_proc_cmdline(pid: int) -> str:
    if sys.platform == 'darwin':
        try:
            return subprocess.check_output(
                ['ps', '-p', str(pid), '-o', 'args='],
                encoding='utf-8',
                stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            return ''

    try:
        raw = Path(f'/proc/{pid}/cmdline').read_bytes()
    except Exception:
        return ''
    return raw.replace(b'\x00', b' ').decode('utf-8', errors='ignore').strip()


def remove_pid_files(paths: tuple[Path, ...]) -> None:
    for path in paths:
        if path.suffix != '.pid':
            continue
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except Exception:
            continue


__all__ = ['read_pid_file', 'read_proc_cmdline', 'read_proc_path', 'remove_pid_files']
