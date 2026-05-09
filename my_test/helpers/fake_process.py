from __future__ import annotations

from subprocess import CompletedProcess


class FakeStdout:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def __iter__(self):
        return iter(self._lines)


class FakeProcess:
    def __init__(self, lines: list[str], returncode: int = 0) -> None:
        self.stdout = FakeStdout(lines)
        self._returncode = returncode

    def wait(self) -> int:
        return self._returncode


class FakePopen:
    def __init__(self, *, lines: list[str], returncode: int = 0) -> None:
        self.calls = []
        self.lines = lines
        self.returncode = returncode

    def __call__(self, argv, cwd, stdout, stderr, text):
        self.calls.append(
            {
                'argv': argv,
                'cwd': cwd,
                'stdout': stdout,
                'stderr': stderr,
                'text': text,
            }
        )
        return FakeProcess(self.lines, self.returncode)


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
