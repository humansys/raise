"""Pytest profiling plugin for RaiSE baseline collection (RAISE-14874).

Activated via ``pytest --profile-baseline[=PATH]``.  When the flag is absent
the plugin is never registered and imposes **zero overhead** on the test run.

Captured data:
- Per-test wall-clock time (setup / call / teardown phases)
- Per-fixture setup + teardown time, grouped by (name, scope)
- Per-module import time during the collection phase (exec_module wall-clock)

Output is a JSON artifact written to *PATH* (default: ``profiling_baseline.json``
in the current directory) on session finish.

Usage::

    pytest packages/raise-cli -n 0 --profile-baseline=work/epics/e14851.../baseline/profiling_baseline.json

See ``work/epics/e14851-test-execution-economy/baseline/README.md`` for full
invocation documentation.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureDef, SubRequest
from _pytest.reports import TestReport

__all__ = [
    "ProfilingPlugin",
    "_FixtureRecord",
    "_ImportTimer",
    "_TimedLoader",
    "pytest_addoption",
    "pytest_configure",
]

_CLI_FLAG = "--profile-baseline"
_PLUGIN_KEY = "raise_profiling_plugin"


# ---------------------------------------------------------------------------
# Module-level hooks (conftest entry-points)
# ---------------------------------------------------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register ``--profile-baseline`` option with pytest."""
    parser.addoption(
        _CLI_FLAG,
        action="store",
        nargs="?",
        const="profiling_baseline.json",
        default=None,
        metavar="OUTPUT",
        help=(
            "Enable profiling baseline collection. "
            "Writes a JSON artifact to OUTPUT. "
            "Defaults to 'profiling_baseline.json' in the current directory."
        ),
    )


def pytest_configure(config: Config) -> None:
    """Register ProfilingPlugin when ``--profile-baseline`` is supplied."""
    output: str | None = config.getoption(_CLI_FLAG, default=None)
    if output is not None:
        plugin = ProfilingPlugin(Path(output))
        config.pluginmanager.register(plugin, _PLUGIN_KEY)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class _FixtureRecord:
    """Accumulator for timing data of a single (fixture_name, scope) bucket.

    Instances are keyed by ``(argname, scope_str)`` inside :class:`ProfilingPlugin`
    and aggregated across all test invocations in a session.
    """

    __slots__ = ("name", "scope", "setup_total", "teardown_total", "call_count")

    def __init__(self, name: str, scope: str) -> None:
        self.name = name
        self.scope = scope
        self.setup_total: float = 0.0
        self.teardown_total: float = 0.0
        self.call_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary matching the artifact schema."""
        return {
            "name": self.name,
            "scope": self.scope,
            "setup_total": round(self.setup_total, 6),
            "teardown_total": round(self.teardown_total, 6),
            "call_count": self.call_count,
        }


# ---------------------------------------------------------------------------
# Import instrumentation
# ---------------------------------------------------------------------------


class _TimedLoader:
    """Wraps an existing module loader to time ``exec_module`` execution.

    Instances are ephemeral: created by :class:`_ImportTimer` inside
    ``find_spec`` and discarded once the module is loaded.
    """

    def __init__(
        self,
        name: str,
        real_loader: Any,
        collector: list[dict[str, Any]],
    ) -> None:
        self._name = name
        self._real = real_loader
        self._collector = collector

    def create_module(self, spec: Any) -> Any:
        """Delegate to the real loader's ``create_module``."""
        if hasattr(self._real, "create_module"):
            return self._real.create_module(spec)
        return None

    def exec_module(self, module: Any) -> None:
        """Execute the module, timing the ``exec_module`` call."""
        start = time.perf_counter()
        if hasattr(self._real, "exec_module"):
            self._real.exec_module(module)
        duration = time.perf_counter() - start
        self._collector.append({"module": self._name, "duration": round(duration, 6)})


class _ImportTimer:
    """``sys.meta_path`` hook that instruments finders to time module loading.

    Install with :meth:`install` before collection and remove with
    :meth:`remove` afterwards.  Captured records are available via
    :attr:`records`.
    """

    def __init__(self) -> None:
        self._collector: list[dict[str, Any]] = []
        self._real_finders: list[Any] = []

    # ------------------------------------------------------------------
    # sys.meta_path protocol
    # ------------------------------------------------------------------

    def find_spec(
        self,
        fullname: str,
        path: Any,
        target: Any = None,
    ) -> Any:
        """Intercept import specs to wrap their loader with :class:`_TimedLoader`.

        Returns ``None`` for already-imported modules so the standard import
        machinery handles them without double-counting.
        """
        if fullname in sys.modules:
            return None

        for finder in self._real_finders:
            if finder is self:
                continue
            if not hasattr(finder, "find_spec"):
                continue
            try:
                spec = finder.find_spec(fullname, path, target)
            except (AttributeError, ImportError, TypeError):
                continue
            if spec is not None and spec.loader is not None:
                spec.loader = _TimedLoader(fullname, spec.loader, self._collector)
                return spec
        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def install(self) -> None:
        """Prepend this finder to ``sys.meta_path``, capturing real finders."""
        self._real_finders = list(sys.meta_path)
        sys.meta_path.insert(0, self)

    def remove(self) -> None:
        """Remove this finder from ``sys.meta_path`` (idempotent)."""
        import contextlib  # noqa: PLC0415

        with contextlib.suppress(ValueError):
            sys.meta_path.remove(self)

    @property
    def records(self) -> list[dict[str, Any]]:
        """Return a snapshot copy of all timed import records."""
        return list(self._collector)


# ---------------------------------------------------------------------------
# Main plugin class
# ---------------------------------------------------------------------------


def _iso_now() -> str:
    """Return current UTC time as ISO-8601 string."""
    from datetime import UTC, datetime  # noqa: PLC0415

    return datetime.now(UTC).isoformat()


class ProfilingPlugin:
    """Pytest plugin collecting per-test, per-fixture, and per-import timings.

    Registered by :func:`pytest_configure` when ``--profile-baseline`` is set.
    Writes a JSON artifact at session finish.
    """

    def __init__(self, output_path: Path) -> None:
        self._output_path = output_path
        self._tests: dict[str, dict[str, Any]] = {}
        self._fixtures: dict[tuple[str, str], _FixtureRecord] = {}
        self._imports: list[dict[str, Any]] = []
        self._session_start: float = 0.0
        self._import_timer: _ImportTimer | None = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def pytest_sessionstart(self, session: pytest.Session) -> None:
        """Record session start time and install the import timer."""
        self._session_start = time.perf_counter()
        self._import_timer = _ImportTimer()
        self._import_timer.install()

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Remove the import timer after collection and store its records."""
        if self._import_timer is not None:
            self._import_timer.remove()
            self._imports = self._import_timer.records

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        """Serialise all collected data to the JSON artifact file."""
        total_wall = round(time.perf_counter() - self._session_start, 6)

        tests_list = list(self._tests.values())
        fixtures_list = [r.to_dict() for r in self._fixtures.values()]

        sorted_tests = sorted(tests_list, key=lambda t: t["total"], reverse=True)
        top10_tests = [
            {"node_id": t["node_id"], "total": t["total"]} for t in sorted_tests[:10]
        ]

        sorted_fixtures = sorted(
            fixtures_list, key=lambda f: f["setup_total"], reverse=True
        )
        top10_fixtures = [
            {
                "name": f["name"],
                "scope": f["scope"],
                "setup_total": f["setup_total"],
            }
            for f in sorted_fixtures[:10]
        ]

        artifact: dict[str, Any] = {
            "meta": {
                "generated_at": _iso_now(),
                "pytest_version": pytest.__version__,
                "platform": platform.node(),
                "workers": 0,
                "packages": ["raise-cli"],
            },
            "tests": tests_list,
            "fixtures": fixtures_list,
            "imports": self._imports,
            "summary": {
                "total_tests": len(tests_list),
                "total_wall_clock": total_wall,
                "top10_slowest_tests": top10_tests,
                "top10_slowest_fixtures": top10_fixtures,
            },
        }

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # Test timing
    # ------------------------------------------------------------------

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Accumulate per-phase durations for each test node."""
        nodeid = report.nodeid
        if nodeid not in self._tests:
            self._tests[nodeid] = {
                "node_id": nodeid,
                "phases": {},
                "total": 0.0,
                "outcome": "passed",
            }
        entry = self._tests[nodeid]
        entry["phases"][report.when] = round(report.duration, 6)
        entry["total"] = round(sum(entry["phases"].values()), 6)
        if report.when == "call":
            entry["outcome"] = report.outcome

    # ------------------------------------------------------------------
    # Fixture timing
    # ------------------------------------------------------------------

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(
        self, fixturedef: FixtureDef[Any], request: SubRequest
    ) -> Any:
        """Wrap fixture setup to record wall-clock time per (name, scope) bucket.

        Also injects teardown timing finalizers into ``fixturedef._finalizers``
        using the LIFO pop() order so that:
        ``_teardown_start`` → fixture teardown code → ``_teardown_end``.

        Note: ``_finalizers`` is a private pytest attribute validated against
        pytest 9.x.  The plugin degrades gracefully if it is unavailable.
        """
        start = time.perf_counter()
        yield
        setup_dur = time.perf_counter() - start

        key: tuple[str, str] = (fixturedef.argname, str(fixturedef.scope))
        if key not in self._fixtures:
            self._fixtures[key] = _FixtureRecord(
                fixturedef.argname, str(fixturedef.scope)
            )
        record = self._fixtures[key]
        record.setup_total += setup_dur
        record.call_count += 1

        # -- Teardown timing via _finalizers (private API) --
        # After setup, fixturedef._finalizers contains the yield-teardown
        # closure (if any).  We want LIFO execution order:
        #   start_timer → fixture_teardown → end_timer
        # Because pop() removes from the END, we need the list arranged as:
        #   [end_timer, fixture_teardown, start_timer]
        # Steps:
        #   1. insert end_timer at index 0  →  [end_timer, <existing>...]
        #   2. append start_timer           →  [end_timer, <existing>..., start_timer]
        finalizers: Any = getattr(fixturedef, "_finalizers", None)
        if isinstance(finalizers, list):
            teardown_start_holder: list[float] = []

            def _teardown_start() -> None:
                teardown_start_holder.append(time.perf_counter())

            def _teardown_end() -> None:
                if teardown_start_holder:
                    record.teardown_total += (
                        time.perf_counter() - teardown_start_holder[0]
                    )

            try:
                finalizers.insert(0, _teardown_end)
                finalizers.append(_teardown_start)
            except (AttributeError, TypeError):
                pass  # degrade gracefully if pytest internals change
