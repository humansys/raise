"""Shared manifest-driven gate runner.

Reads a command from ``.raise/manifest.yaml`` and executes it via subprocess.
All built-in gates delegate to this helper for DRY command execution.

Architecture: S474.2 — Configurable Gates + FormatGate
"""

from __future__ import annotations

import contextlib
import logging
import os
import shlex
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from raise_cli.gates import worker_budget
from raise_cli.gates.execution_ledger import (
    ExecutionOutcome,
    ExecutionStatus,
    complete,
    find_active,
    register,
)
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.project_config.manifest import load_manifest

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from raise_cli.project_config.manifest import AppInfo

_COMMAND_KEYS: tuple[str, ...] = (
    "test_command",
    "type_check_command",
    "lint_command",
    "format_command",
)

_NODE_TOOLS: frozenset[str] = frozenset({"npm", "npx", "node", "vitest", "tsc"})


def _recovery_hint(exe: str) -> str:
    if exe in _NODE_TOOLS:
        return "install Node.js from https://nodejs.org"
    return f"add '{exe}' to PATH"


def check_app_executables(
    apps: list[AppInfo],
    manifest_keys: tuple[str, ...] = _COMMAND_KEYS,
) -> GateResult | None:
    """Return a failed GateResult when any app declares an unavailable executable.

    Scans each app's configured commands for the first executable token and
    verifies it via shutil.which. Returns None when all are present so callers
    can use ``if result := check_app_executables(apps): return result``.
    """
    missing: list[str] = []
    seen: set[tuple[str, str]] = set()
    for app in apps:
        for key in manifest_keys:
            command: str | None = getattr(app, key, None)
            if not command:
                continue
            tokens = shlex.split(command)
            if not tokens:
                continue
            exe = tokens[0]
            pair = (app.name, exe)
            if pair in seen:
                continue
            seen.add(pair)
            if shutil.which(exe) is None:
                missing.append(
                    f"[{app.name}/{key}] '{exe}' not found — {_recovery_hint(exe)}"
                )
    if not missing:
        return None
    return GateResult(
        passed=False,
        gate_id="gate-preflight",
        message=(
            f"Preflight: {len(missing)} missing executable(s) — "
            "install them before running the gate suite"
        ),
        details=tuple(missing),
    )


def _resolve_argv(tokens: list[str]) -> list[str]:
    """Resolve the executable via ``shutil.which`` for Windows PATHEXT compat."""
    if not tokens:
        return tokens
    exe = shutil.which(tokens[0])
    if exe is not None:
        return [exe, *tokens[1:]]
    return tokens


def test_env(manifest_key: str, working_dir: Path) -> dict[str, str] | None:
    """Per-invocation COVERAGE_FILE namespacing for test commands (S8170.1).

    Concurrent suites writing to the same .coverage default corrupt each
    other via pytest-cov auto-combine (pytest-cov #416). Returns an env
    with a unique COVERAGE_FILE under working_dir, or None when the
    command is not a test run or the caller already set COVERAGE_FILE.
    """
    if manifest_key != "test_command" or "COVERAGE_FILE" in os.environ:
        return None
    env = dict(os.environ)
    env["COVERAGE_FILE"] = str(working_dir / f".coverage.gate-{uuid4().hex[:8]}")
    return env


def worker_args(manifest_key: str) -> tuple[str, ...]:
    """Bound xdist workers for test-command gates (RAISE-10439 / E10436).

    Concurrent agents each launching ``-n auto`` (one worker per core)
    oversubscribe the CPU: N agents × cores workers on cores cores. When
    ``RAISE_TEST_WORKERS`` is set, test-command gates pass ``-n {value}``,
    which overrides the ``-n auto`` in addopts (the later ``-n`` wins). Returns
    no extra args for non-test commands or when the env var is unset/blank, so
    local and MR/CI runs keep ``-n auto``.
    """
    if manifest_key != "test_command":
        return ()
    value = os.environ.get("RAISE_TEST_WORKERS", "").strip()
    if not value:
        return ()
    return ("-n", value)


@contextlib.contextmanager
def worker_lease(manifest_key: str) -> Iterator[tuple[str, ...]]:
    """Yield the ``-n`` tokens for a gate subprocess, holding a worker-budget lease.

    Layered over :func:`worker_args` (RAISE-10544 / E10436):

    - Non-test commands and an explicit ``RAISE_TEST_WORKERS`` bypass the budget
      and use :func:`worker_args` directly — the explicit value is the user's
      exact choice and stays per-process.
    - Otherwise the cross-process :mod:`worker_budget` governor decides: a lone
      run keeps ``-n auto`` (yields no tokens), while a run that starts while
      another holds budget is bounded to the remaining cores so concurrent
      agents stop oversubscribing the CPU. The lease is held for the duration of
      the block (i.e. the subprocess) and released on exit.
    """
    if (
        manifest_key != "test_command"
        or os.environ.get("RAISE_TEST_WORKERS", "").strip()
    ):
        yield worker_args(manifest_key)
        return
    with worker_budget.lease(worker_budget.total_budget()) as grant:
        yield ("-n", str(grant.workers)) if grant.bounded else ()


def cleanup_coverage_files(env: dict[str, str] | None) -> None:
    """Remove the namespaced coverage file and its parallel-mode suffixes."""
    if env is None or "COVERAGE_FILE" not in env:
        return
    base = Path(env["COVERAGE_FILE"])
    with contextlib.suppress(OSError):
        for leftover in base.parent.glob(base.name + "*"):
            leftover.unlink(missing_ok=True)


def run_manifest_command(
    gate_id: str,
    manifest_key: str,
    description: str,
    context: GateContext,
) -> GateResult:
    """Read a command from manifest and execute it.

    When the manifest contains an ``apps`` list, each app's command is executed
    independently and results are aggregated.  If no apps are defined, the
    root-level command is used (original single-app behavior).

    Args:
        gate_id: Unique gate identifier (e.g. ``"gate-tests"``).
        manifest_key: Attribute name on ``ProjectInfo`` (e.g. ``"test_command"``).
        description: Human-readable description for pass messages.
        context: Gate evaluation context with working directory.

    Returns:
        GateResult with pass/fail/skip outcome.
    """
    manifest = load_manifest(context.working_dir)
    if manifest is None:
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message="No .raise/manifest.yaml found",
        )

    # --- Per-app execution when apps are configured ---
    if manifest.project.apps:
        return _run_per_app(
            gate_id=gate_id,
            manifest_key=manifest_key,
            description=description,
            apps=manifest.project.apps,
            working_dir=context.working_dir,
            extra_args=context.extra_args,
            root_test_command=getattr(manifest.project, manifest_key, None)
            if manifest_key == "test_command"
            else None,
        )

    # --- Single-app (root command) ---
    return _run_single(
        gate_id=gate_id,
        manifest_key=manifest_key,
        description=description,
        command=getattr(manifest.project, manifest_key, None),
        working_dir=context.working_dir,
        extra_args=context.extra_args,
    )


PYTEST_NO_TESTS_COLLECTED = 5
"""pytest's exit code for "no tests were collected"."""


def _is_pytest(command: str) -> bool:
    """Whether *command* invokes pytest (so exit 5 means "no tests collected")."""
    return "pytest" in shlex.split(command)


def _collected_nothing(command: str, returncode: int) -> bool:
    """Whether the run ended with pytest's zero-tests-collected signal."""
    return returncode == PYTEST_NO_TESTS_COLLECTED and _is_pytest(command)


def _head_sha(working_dir: Path) -> str:
    """Resolve HEAD commit SHA for cache invalidation.

    Uses Popen directly — tests mock subprocess.run (and check_output
    delegates to run in Python 3.13+), so both would be intercepted.
    """
    try:
        proc = subprocess.Popen(
            ["git", "rev-parse", "HEAD"],
            cwd=str(working_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        out, _ = proc.communicate(timeout=5)
        return out.strip()[:12] if proc.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def _ledger_scope(extra_args: tuple[str, ...], working_dir: Path | None = None) -> str:
    """Build the ledger deduplication scope from extra_args and HEAD SHA."""
    parts = list(extra_args)
    if working_dir is not None:
        sha = _head_sha(working_dir)
        if sha:
            parts.append(f"@{sha}")
    return " ".join(parts)


def _check_ledger(gate_id: str, working_dir: Path, scope: str) -> GateResult | None:
    """Return cached GateResult from the execution ledger, or None."""
    entry = find_active(gate_id, str(working_dir), scope)
    if entry is None:
        return None
    if entry.status == ExecutionStatus.COMPLETED and entry.result is not None:
        _log.info(
            "gate %s: returning cached outcome (execution %s)",
            gate_id,
            entry.execution_id,
        )
        return GateResult(
            passed=entry.result.passed,
            gate_id=gate_id,
            message=entry.result.message,
            details=entry.result.details,
        )
    if entry.pid != os.getpid():
        _log.warning(
            "gate %s: another process (pid %d) is running this gate — "
            "returning in-flight status",
            gate_id,
            entry.pid,
        )
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message=(
                f"Gate {gate_id} is already running in pid {entry.pid}; "
                f"wait for it to complete or reap the stale execution"
            ),
        )
    return None


def _record_outcome(execution_id: str, gate_result: GateResult) -> None:
    """Persist a gate result into the execution ledger."""
    complete(
        execution_id,
        ExecutionOutcome(
            passed=gate_result.passed,
            message=gate_result.message,
            details=gate_result.details,
        ),
    )


def _run_single(
    *,
    gate_id: str,
    manifest_key: str,
    description: str,
    command: str | None,
    working_dir: Path,
    extra_args: tuple[str, ...] = (),
) -> GateResult:
    """Execute a single command and return the gate result."""
    if command is None:
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"Skipped — {manifest_key} not configured",
        )

    use_ledger = manifest_key == "test_command"

    if use_ledger:
        scope = _ledger_scope(extra_args, working_dir)
        cached = _check_ledger(gate_id, working_dir, scope)
        if cached is not None:
            return cached
        execution_id = register(gate_id, str(working_dir), scope)
    else:
        scope = ""
        execution_id = ""

    env = test_env(manifest_key, working_dir)
    try:
        with worker_lease(manifest_key) as nflags:
            result = subprocess.run(
                _resolve_argv([*shlex.split(command), *nflags, *extra_args]),
                capture_output=True,
                text=True,
                cwd=str(working_dir),
                env=env,
            )
    except Exception as exc:  # noqa: BLE001
        gate_result = GateResult(
            passed=False,
            gate_id=gate_id,
            message=f"{type(exc).__name__}: {exc}",
        )
        if use_ledger:
            _record_outcome(execution_id, gate_result)
        return gate_result
    finally:
        cleanup_coverage_files(env)

    passed = result.returncode == 0
    if _collected_nothing(command, result.returncode):
        message = "No tests collected — gate verified nothing"
    else:
        message = description if passed else f"{description} failed"
    gate_result = GateResult(
        passed=passed,
        gate_id=gate_id,
        message=message,
        details=tuple(s for s in (result.stdout, result.stderr) if s)
        if not passed
        else (),
    )
    if use_ledger:
        _record_outcome(execution_id, gate_result)
    return gate_result


def _scoped_tokens(command: str, scope_prefix: str | None) -> list[str]:
    """Split a command, substituting path tokens the scope refines.

    The scope replaces the app's own path token (e.g. the trailing
    ``packages/raise-cli`` testpath) — appending both would make pytest
    run the union, i.e. the whole package (RAISE-8162). Tokens embedding
    paths in flags (``--ignore=...``) never match and are preserved.
    """
    tokens = shlex.split(command)
    if not scope_prefix:
        return tokens
    return [
        t
        for t in tokens
        if not (scope_prefix == t or scope_prefix.startswith(t.rstrip("/") + "/"))
    ]


def _app_ledger_key(app_name: str) -> str:
    return f"gate-tests:{app_name}"


def _record_app_outcome(
    execution_id: str,
    app_name: str,
    description: str,
    result: subprocess.CompletedProcess[str],
) -> None:
    """Record a per-app gate outcome in the execution ledger."""
    _record_outcome(
        execution_id,
        GateResult(
            passed=result.returncode == 0,
            gate_id=_app_ledger_key(app_name),
            message=description if result.returncode == 0 else f"{description} failed",
            details=tuple(
                f"[{app_name}] {o}" for o in (result.stdout, result.stderr) if o
            ),
        ),
    )


def _app_ledger_check(
    app_name: str,
    manifest_key: str,
    working_dir: Path,
    extra_args: tuple[str, ...],
    failures: list[str],
    all_details: list[str],
) -> tuple[bool, str, bool]:
    """Check the ledger for a per-app gate; return (handled, execution_id, use_ledger)."""
    if manifest_key != "test_command":
        return False, "", False
    app_scope = f"{app_name}:{_ledger_scope(extra_args, working_dir)}"
    cached = _check_ledger(_app_ledger_key(app_name), working_dir, app_scope)
    if cached is not None:
        if not cached.passed:
            failures.append(f"[{app_name}] {cached.message}")
            all_details.extend(cached.details)
        return True, "", True
    execution_id = register(_app_ledger_key(app_name), str(working_dir), app_scope)
    return False, execution_id, True


def _run_one_app(  # noqa: C901
    *,
    app: AppInfo,
    manifest_key: str,
    description: str,
    scope_prefix: str | None,
    working_dir: Path,
    extra_args: tuple[str, ...],
    failures: list[str],
    all_details: list[str],
) -> bool:
    """Execute one app's gate command and accumulate results.

    Returns True if the app ran (i.e. it was not skipped), False otherwise.
    """
    command: str | None = getattr(app, manifest_key, None)
    if command is None:
        return False

    if scope_prefix and not scope_prefix.startswith(app.path):
        return False

    handled, execution_id, use_ledger = _app_ledger_check(
        app.name, manifest_key, working_dir, extra_args, failures, all_details
    )
    if handled:
        return True

    env = test_env(manifest_key, working_dir)
    try:
        with worker_lease(manifest_key) as nflags:
            result = subprocess.run(
                _resolve_argv(
                    [
                        *_scoped_tokens(command, scope_prefix),
                        *nflags,
                        *extra_args,
                    ]
                ),
                capture_output=True,
                text=True,
                cwd=str(working_dir),
                env=env,
            )
    except FileNotFoundError as exc:
        # Preflight should have caught this; treat it as an explicit failure
        # rather than a silent skip so callers never see a false green (RAISE-17041).
        # Clear rather than record so a retry after installing the missing tool
        # isn't blocked by a stale cached failure (unlike the generic Exception path).
        _log.warning(
            "[%s] toolchain not found: %s",
            app.name,
            exc,
        )
        failures.append(f"[{app.name}] toolchain not found: {exc}")
        if use_ledger:
            from raise_cli.gates.execution_ledger import clear_for_key

            clear_for_key(
                _app_ledger_key(app.name),
                str(working_dir),
                f"{app.name}:{_ledger_scope(extra_args, working_dir)}",
            )
        return True
    except Exception as exc:  # noqa: BLE001
        failures.append(f"[{app.name}] {type(exc).__name__}: {exc}")
        if use_ledger:
            _record_outcome(
                execution_id,
                GateResult(
                    passed=False,
                    gate_id=_app_ledger_key(app.name),
                    message=f"{type(exc).__name__}: {exc}",
                ),
            )
        return True
    finally:
        cleanup_coverage_files(env)

    if result.returncode != 0:
        failures.append(f"[{app.name}] {description} failed")
        for output in (result.stdout, result.stderr):
            if output:
                all_details.append(f"[{app.name}] {output}")

    if use_ledger:
        _record_app_outcome(execution_id, app.name, description, result)

    return True


def _normalize_scope(scope: str, working_dir: Path) -> str:
    """Return *scope* as a path relative to *working_dir*.

    Handles absolute paths and ``./``-prefixed relative paths so that both
    the app-filter and :func:`_scoped_tokens` receive a plain relative token
    (e.g. ``packages/raise-cli/tests/foo.py``).  If *scope* cannot be made
    relative to *working_dir* (out-of-tree path) it is returned unchanged so
    that the app-filter will skip all apps rather than silently misbehave.
    (RAISE-8026)
    """
    with contextlib.suppress(ValueError):
        return str(Path(scope).resolve().relative_to(working_dir.resolve()))
    return scope


def _run_scope_fallback(
    *, gate_id: str, scope: str, working_dir: Path, root_test_command: str | None
) -> GateResult:
    """Run the project test command on an explicit *scope* that matched no configured app.

    Without this, ``gate-tests --scope <path-outside-apps>`` returned a silent
    green ("Skipped"), giving false confidence that tests ran. Validation/PoC
    tests under ``work/`` live outside ``packages/`` app roots; this fallback
    verifies them honestly instead of a false skip (RAISE-14120). pytest exit
    code 5 (no tests collected) is reported as a non-failing "no tests" outcome
    — explicit, not the misleading "not configured in any app" skip.

    Uses the project-level ``test_command`` from the manifest so that non-Python
    and custom-toolchain projects are respected (RAISE-16928). Falls back to the
    legacy hardcoded pytest invocation only when ``test_command`` is not set.
    """
    if root_test_command is not None:
        command = [*shlex.split(root_test_command), scope]
    else:
        command = ["uv", "run", "pytest", "--tb=short", scope]
    env = test_env("test_command", working_dir)
    try:
        with worker_lease("test_command") as nflags:
            result = subprocess.run(
                _resolve_argv([*command, *nflags]),
                capture_output=True,
                text=True,
                cwd=str(working_dir),
                env=env,
            )
    except Exception as exc:  # noqa: BLE001
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message=f"scope fallback {type(exc).__name__}: {exc}",
        )
    finally:
        cleanup_coverage_files(env)

    if result.returncode == PYTEST_NO_TESTS_COLLECTED:
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message=f"No tests collected at scope: {scope}",
        )
    if result.returncode != 0:
        details = tuple(o for o in (result.stdout, result.stderr) if o)
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message=f"Tests failed at scope: {scope}",
            details=details,
        )
    return GateResult(
        passed=True,
        gate_id=gate_id,
        message=f"Tests pass (scope: {scope})",
    )


def _run_per_app(
    *,
    gate_id: str,
    manifest_key: str,
    description: str,
    apps: list[AppInfo],
    working_dir: Path,
    extra_args: tuple[str, ...] = (),
    root_test_command: str | None = None,
) -> GateResult:
    """Execute gate command for each app and aggregate results.

    When extra_args contains a scope path, only apps whose test_command
    contains the scope prefix are run — other apps are skipped silently.
    This prevents --scope packages/raise-cli/... from also running
    raise-server tests.
    """
    # Preflight: verify declared executables before launching any subprocess.
    preflight = check_app_executables(apps, manifest_keys=(manifest_key,))
    if preflight is not None:
        return preflight

    failures: list[str] = []
    all_details: list[str] = []
    ran_any = False

    # If a scope path is given (first extra_arg), skip apps whose root path
    # is not a prefix of the scope — prevents raise-server running when
    # scope is packages/raise-cli/tests/... (RAISE-2962 regression fix).
    scope_prefix: str | None = extra_args[0] if extra_args else None

    # Normalize scope to a relative path so absolute and ./-prefixed inputs
    # work correctly with both the app filter and _scoped_tokens (RAISE-8026).
    if scope_prefix:
        scope_prefix = _normalize_scope(scope_prefix, working_dir)

    for app in apps:
        if _run_one_app(
            app=app,
            manifest_key=manifest_key,
            description=description,
            scope_prefix=scope_prefix,
            working_dir=working_dir,
            extra_args=extra_args,
            failures=failures,
            all_details=all_details,
        ):
            ran_any = True

    if not ran_any:
        # An explicit test scope that matched no configured app used to return a
        # silent green ("Skipped"), giving false confidence that tests ran. Run a
        # fallback pytest on that scope instead so validation/PoC tests under
        # work/ are actually verified (RAISE-14120). Only the tests gate falls
        # back — lint/format/types stay strictly per-app.
        if scope_prefix and manifest_key == "test_command":
            return _run_scope_fallback(
                gate_id=gate_id,
                scope=scope_prefix,
                working_dir=working_dir,
                root_test_command=root_test_command,
            )
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"Skipped — {manifest_key} not configured in any app",
        )

    if failures:
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message="; ".join(failures),
            details=tuple(all_details),
        )

    return GateResult(
        passed=True,
        gate_id=gate_id,
        message=description,
    )
