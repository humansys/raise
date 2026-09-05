"""Storage test suite conftest."""

from __future__ import annotations

import signal
import sys

import pytest


def pytest_sessionstart(session: pytest.Session) -> None:
    if sys.platform == "win32":
        # The GitHub Actions Windows runner delivers a spurious SIGINT to the
        # process group at roughly T+80s from job start (from a prior step's
        # subprocess cleanup interacting with the Windows console group).
        # This causes a KeyboardInterrupt in whichever SQLite operation is
        # in progress at that moment — schema.executescript releases the GIL,
        # so the pending signal fires at the next opcode check.
        #
        # These storage tests are non-interactive and complete in <40s, so
        # suppressing SIGINT for the duration of this session is safe.
        # pytest_sessionstart runs after all plugins (including TerminalReporter)
        # have installed their own handlers, making this the final handler.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
