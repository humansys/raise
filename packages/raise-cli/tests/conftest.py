"""Global test fixtures.

Prevents test leakage into real ~/.rai/developer.yaml by redirecting
get_rai_home to a temporary directory for ALL tests.
"""

# pyright: reportUnusedFunction=false

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Tier-marker auto-tagging (RAISE-14910)
# ---------------------------------------------------------------------------
# Tests that carry none of the declared tier markers are implicitly unit tests
# (fast, isolated, no external I/O). We attach @pytest.mark.unit automatically
# so the marker census always reports 0 unclassified tests without requiring
# every author to type it manually.
_TIER_MARKERS = frozenset({"unit", "integration", "slow", "ml", "e2e", "perf"})


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Auto-apply ``@pytest.mark.unit`` to tests with no explicit tier marker."""
    unit_mark = pytest.mark.unit
    for item in items:
        effective_markers = {m.name for m in item.iter_markers()}
        if not effective_markers & _TIER_MARKERS:
            item.add_marker(unit_mark, append=True)


@pytest.fixture(autouse=True)
def _disable_rich_colors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable Rich/Typer ANSI output in CLI tests.

    Without this, help output contains ANSI escape codes that break
    string-match assertions (e.g. assert '--context' in result.output).
    """
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("TERM", "dumb")


@pytest.fixture(autouse=True)
def _block_graph_build_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block `python -m raise_cli graph build` in child processes.

    Sets the sentinel inherited by subprocesses so __main__ exits 86
    instead of invoking real ML inference or mutating checkout cartridges.
    Kept separate from _disable_rich_colors to make the intent explicit
    and prevent silent breakage if that fixture is refactored.
    """
    monkeypatch.setenv("RAISE_TEST_BLOCK_GRAPH_BUILD", "1")
    monkeypatch.setenv("RAISE_CARTRIDGE_EMBED", "0")


@pytest.fixture(autouse=True)
def _isolate_server_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent DualWriteBackend and ApiSessionContextBackend from activating.

    Without this, tests that invoke graph build (or any code path through
    get_active_backend / get_session_context_backend) will attempt remote
    sync when the developer's shell has these set.
    """
    monkeypatch.delenv("RAI_SERVER_URL", raising=False)
    monkeypatch.delenv("RAI_API_KEY", raising=False)
    monkeypatch.delenv("RAISE_SERVER_URL", raising=False)
    monkeypatch.delenv("RAISE_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def _isolate_agent_session_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent a runtime's ambient session ID from leaking into test fixtures.

    Tests that exercise runtime-agnostic session discovery set their own value
    explicitly. All other tests must remain independent of the process that
    launched pytest (for example Cockpit setting ``RAISE_AGENT_SESSION_ID``).
    """
    monkeypatch.delenv("RAISE_AGENT_SESSION_ID", raising=False)
    monkeypatch.delenv("RAISE_CC_SESSION_ID", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)


@pytest.fixture(autouse=True)
def _mcp_cwd_guard_inert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep pre-S15457.2 resolution semantics in the legacy suite.

    Checkout-scoped MCP tools now require an explicit caller ``cwd``
    (fail-loud ``cwd_required`` in community stdio mode, S15457.2). Tests
    written before the guard rely on the server-CWD fallback; replacing the
    guard with the exact pre-guard behavior preserves that. The guard's own
    tests (tests/pipeline/test_mcp_caller_context.py and the per-tool
    regression tests) re-install the real implementations explicitly.
    """

    def _legacy_require(cwd: str, tool: str) -> Path:  # noqa: ARG001
        return Path(cwd).resolve() if cwd else Path.cwd()

    def _legacy_resolve_run(cwd: str, start_cwd: str, tool: str) -> Path:  # noqa: ARG001
        if cwd:
            return Path(cwd)
        if start_cwd:
            return Path(start_cwd)
        return Path.cwd()

    monkeypatch.setattr(
        "raise_cli.pipeline._caller_context.require_caller_cwd", _legacy_require
    )
    monkeypatch.setattr(
        "raise_cli.pipeline._caller_context.resolve_run_cwd", _legacy_resolve_run
    )


@pytest.fixture(autouse=True)
def _isolate_rai_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect all RAI home resolution to tmp_path for every test.

    Without this, tests that call get_project_db() or get_global_db()
    write to ~/.rai/projects/{hash}/raise.db, polluting the real home
    directory with hundreds of empty DBs per test run.
    """
    fake_rai_home = tmp_path / ".rai"
    monkeypatch.setenv("RAI_HOME", str(fake_rai_home))
    monkeypatch.setattr(
        "raise_cli.developer_profile.profile.get_rai_home", lambda: fake_rai_home
    )
    monkeypatch.setattr(
        "raise_cli.developer_profile.persistence.get_rai_home", lambda: fake_rai_home
    )
    # setattr (not env) so tests using patch.dict(os.environ, clear=True)
    # cannot accidentally resolve the developer's real ~/.rai/server.json.
    monkeypatch.setattr(
        "raise_cli.config.server.get_global_rai_dir", lambda: fake_rai_home
    )
    from raise_cli.storage.connection import get_project_hash

    get_project_hash.cache_clear()


@pytest.fixture(autouse=True)
def _isolate_pm_adapter(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Block real PM adapter resolution (Jira/etc.) during tests.

    Without this, code paths that call resolve_pm_adapter() in-process
    (e.g. `rai mission new`) resolve the real JiraAdapter from the
    developer's `.raise/backlog.yaml` and create real issues in prod Jira
    when tests run via CliRunner (RAISE-14069).

    Opt out with `@pytest.mark.real_pm_resolution` for tests that
    exercise the resolver itself against a stubbed discovery layer.
    """
    if request.node.get_closest_marker("real_pm_resolution"):
        return

    from raise_cli.exceptions import AdapterResolutionError

    def _blocked_resolve_pm_adapter(*_args: object, **_kwargs: object) -> object:
        raise AdapterResolutionError(
            "resolve_pm_adapter() blocked under pytest (RAISE-14069): "
            "real adapter resolution is disabled in tests to prevent "
            "writes to production PM systems. Mock the call site or mark "
            "the test with @pytest.mark.real_pm_resolution."
        )

    monkeypatch.setattr(
        "raise_cli.adapters.resolve.resolve_pm_adapter",
        _blocked_resolve_pm_adapter,
    )


@pytest.fixture(autouse=True)
def _reset_error_console() -> Generator[None, None, None]:
    """Reset the cli_error() singleton before and after each test.

    test_error_handler.py::TestHandleErrorReturnValue.setup_method sets
    _error_console = Console(file=io.StringIO()) with no teardown. With
    -n 4 --dist loadscope, when that module shares a worker with CLI command
    tests, the stale StringIO console silences all cli_error() output,
    making result.output == '' and breaking error-path assertions (RAISE-14896).
    """
    from raise_cli.cli.error_handler import set_error_console

    set_error_console(None)
    yield
    set_error_console(None)


@pytest.fixture(autouse=True)
def _restore_cwd() -> Generator[None, None, None]:
    """Snapshot CWD before each test and restore it after.

    Some tests use bare `os.chdir(tmp_path)` (not monkeypatch.chdir). If they
    fail between chdir and the restore line, CWD leaks into later tests.
    Pipeline MCP tests use `Path.cwd().glob(...)` for artifact discovery; a
    leaked CWD pointing at a disposed tmp_path returns empty globs and breaks
    gate assertions (status="artifact_missing" instead of "gate_pending").
    """
    cwd = os.getcwd()
    yield
    os.chdir(cwd)
