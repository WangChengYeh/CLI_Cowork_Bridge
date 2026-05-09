from __future__ import annotations

from subprocess import CompletedProcess


class FakeStdout:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def __iter__(self):
        return iter(self._lines)


class FakeProcess:
    def __init__(self, lines: list[str], returncode: int = 0, pid: int = 4321) -> None:
        self.stdout = FakeStdout(lines)
        self._returncode = returncode
        self.pid = pid

    def wait(self) -> int:
        return self._returncode


class FakePopen:
    def __init__(self, *, lines: list[str] | None = None, returncode: int = 0, pid: int = 4321) -> None:
        self.calls = []
        self.lines = lines or []
        self.returncode = returncode
        self.pid = pid

    def __call__(self, argv, cwd, stdout=None, stderr=None, stdin=None, start_new_session=False, text=True):
        self.calls.append(
            {
                'argv': argv,
                'cwd': cwd,
                'stdout': stdout,
                'stderr': stderr,
                'stdin': stdin,
                'start_new_session': start_new_session,
                'text': text,
            }
        )
        return FakeProcess(self.lines, self.returncode, self.pid)


class FakeRun:
    def __init__(self, *, returncode: int, stdout: str = '', stderr: str = '') -> None:
        self.calls = []
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, argv, cwd, capture_output, text):
        self.calls.append(
            {
                'argv': argv,
                'cwd': cwd,
                'capture_output': capture_output,
                'text': text,
            }
        )
        return CompletedProcess(
            args=argv,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )
