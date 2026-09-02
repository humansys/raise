"""Composite task-complete service — S8370.1 (E8370 K1, ADR-093/ADR-024).

Collapses the inner task loop (gates + branch-assert + add + commit + signal)
into a single in-process call. Mirrors the S7884.3 story bookend pattern one
level down: one ``CheckResult`` per deterministic step, block-propagation,
``_skipped_result`` for every step after the first block.

Shared utilities imported as-is from ``session/open_service.py`` — no
clone amplification (AG2 guard from design doc).
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from pydantic import BaseModel

from raise_cli.gates.execution import derive_test_scopes as derive_test_scopes
from raise_cli.gates.execution import resolve_effective_scopes, run_gate_set
from raise_cli.gates.execution import types_scope_for as _types_scope
from raise_cli.git.branch_guard import assert_head_branch
from raise_cli.onboarding.manifest import load_manifest
from raise_cli.session.open_service import STATUS_RANK, CheckResult, run_git
from raise_cli.telemetry.trailer import resolve_session_id, with_session_trailer

# Re-export compat (RAISE-13749 T7) — derive_test_scopes/resolve_effective_scopes/
# _types_scope moved to gates/execution.py (the seam's scope-derive, reused from
# RAISE-10440/E10436). Re-exported under the original names so existing callers
# and tests (tests/task/test_complete_service.py) keep resolving with zero edits.
# Retire this shim in S3/S7 cleanup once nothing imports the old path.


class TaskCompleteReport(BaseModel):
    """Composite result of a task-complete call: one CheckResult per step.

    Top-level clarity fields (RAISE-15493 F1 — response-contract fix):
    - ``committed`` — True only when the commit step produced a sha; False on
      any block (gates, branch, stage, commit).  Never infer from step statuses
      alone: a skipped commit returns status="ok" but produced no sha.
    - ``blocking_gate`` — name of the first step that blocked ("gates",
      "branch", …), or None when all steps passed.
    - ``remediation`` — a single action string for the caller when blocked,
      or None on success.  Derived from ``blocking_gate`` + blocked-step data;
      never requires inspecting nested ``CheckResult.data.failures``.
    """

    status: str  # ok | warn | blocked (worst step) — unchanged
    committed: bool = False  # True iff commit step produced a sha
    blocking_gate: str | None = None  # first blocked step name, else None
    remediation: str | None = None  # unambiguous action string when blocked
    gates: CheckResult
    branch: CheckResult
    stage: CheckResult
    commit: CheckResult
    signal: CheckResult


def _skipped_result(name: str) -> CheckResult:
    """Return a skipped CheckResult — used when a prior step blocked."""
    return CheckResult(name=name, status="ok", data={"skipped": True})


def _worst_status(checks: list[CheckResult]) -> str:
    """Return the worst status across a list of CheckResults."""
    return max(checks, key=lambda c: STATUS_RANK[c.status]).status


def _remediation_for(step: CheckResult) -> str | None:
    """Derive a single unambiguous action string from a blocked CheckResult.

    Returns None when the step is not blocked.  The string is machine-readable
    (stable prefix) and human-readable (describes the fix).  Parsing
    ``step.data["failures"]`` to distinguish lint / types / tests avoids
    adding per-gate enums while keeping specificity (SbE table in design doc).
    """
    if step.status != "blocked":
        return None
    if step.name == "gates":
        failures: list[str] = list(step.data.get("failures") or [])
        if any("gate-lint" in f for f in failures):
            return "lint gate blocked — run ruff and fix violations before committing"
        if any("gate-types" in f for f in failures):
            return "type gate blocked — pyright violations must be resolved"
        if any("gate-tests" in f for f in failures):
            return "test gate blocked — all tests must pass before commit"
        if any("gate-format" in f for f in failures):
            return "format gate blocked — run ruff format before committing"
        return "gate blocked — fix all gate violations before committing"
    if step.name == "branch":
        return "branch mismatch — checkout the story branch before committing"
    if step.name == "stage":
        return "stage failed — check file paths in the 'files' argument"
    if step.name == "commit":
        return "commit failed — check git state before committing"
    return f"{step.name} blocked — check {step.name} configuration"


# ---------------------------------------------------------------------------
# Step functions — each returns a CheckResult(name, status, data)
# ---------------------------------------------------------------------------


def _collect_compliance_scopes(files: str, project_path: Path) -> list[str]:
    """Return additional test scopes required by protocol_compliance manifest config.

    When a task modifies a file that matches a declared pattern, the corresponding
    compliance scopes must also run — regardless of gate_scope (RAISE-8109).
    Returns empty list when files is empty, manifest is absent, or no pattern matches.
    """
    if not files:
        return []
    manifest = load_manifest(project_path)
    if manifest is None or not manifest.protocol_compliance:
        return []
    seen: set[str] = set()
    additional: list[str] = []
    for entry in manifest.protocol_compliance:
        # Use suffix match to avoid false positives (e.g. "protocols_v2.py"
        # matching a pattern of "protocols.py").
        if any(f.endswith(entry.pattern) for f in files.split()):
            for scope in entry.scopes:
                if scope not in seen:
                    seen.add(scope)
                    additional.append(scope)
    return additional


def _changed_files(cwd: Path) -> list[str]:
    """Tracked + untracked changed files in the working tree (pre-commit).

    At task-complete time the work is unstaged/staged but not yet committed
    (staging happens after the gates step), so ``git diff --name-only HEAD``
    captures tracked edits and ``ls-files --others`` captures new files.
    """
    out: list[str] = []
    diff = run_git(cwd, "diff", "--name-only", "HEAD")
    if diff is not None and diff.returncode == 0:
        out.extend(diff.stdout.split())
    others = run_git(cwd, "ls-files", "--others", "--exclude-standard")
    if others is not None and others.returncode == 0:
        out.extend(others.stdout.split())
    return out


def _run_scoped_gates(cwd: Path, gate_scope: str) -> CheckResult:
    """Run gate-tests, gate-lint, gate-format, gate-types in-process.

    Delegates to run_gate_set(specs, cwd) — the gate-execution seam
    (RAISE-13749 T11). Bare scope path, no --scope token (D2 from design
    doc). gate-types is scoped to the package ``src`` (never the raw test
    path) so it matches the canonical project type check (see
    ``_types_scope``). An unregistered gate id now surfaces as an explicit
    ``GateSkip`` in ``CheckResult.data["skips"]`` instead of silently
    vanishing (the direct fix for the former ``continue``-past-missing-gate
    here).
    """
    gate_ids = ("gate-tests", "gate-lint", "gate-format", "gate-types")
    extra_args: tuple[str, ...] = (gate_scope,) if gate_scope else ()
    types_scope = _types_scope(gate_scope)
    types_args: tuple[str, ...] = (types_scope,) if types_scope else ()

    specs = tuple(
        (gate_id, types_args if gate_id == "gate-types" else extra_args)
        for gate_id in gate_ids
    )
    report = run_gate_set(specs, cwd)

    failures = [f"{r.gate_id}: {r.message}" for r in report.failures]
    all_details = [d for r in report.failures for d in r.details]
    skips = [{"gate_id": s.gate_id, "reason": s.reason} for s in report.skips]

    if failures:
        data: dict[str, object] = {"failures": failures, "details": all_details}
        if skips:
            data["skips"] = skips
        return CheckResult(name="gates", status="blocked", data=data)
    if skips:
        return CheckResult(name="gates", status="ok", data={"skips": skips})
    return CheckResult(name="gates", status="ok", data={})


def _assert_branch(cwd: Path, expected_branch: str) -> CheckResult:
    """Assert current branch matches expected_branch — read-only, no git mutation."""
    proc = run_git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="branch",
            status="blocked",
            data={"reason": "git-unavailable"},
        )
    current = proc.stdout.strip()
    if current != expected_branch:
        return CheckResult(
            name="branch",
            status="blocked",
            data={
                "reason": "wrong-branch",
                "current": current,
                "expected": expected_branch,
            },
        )
    return CheckResult(name="branch", status="ok", data={"branch": current})


def _git_stage(cwd: Path, files: str) -> CheckResult:
    """Stage files for commit — ``git add {files}`` or ``git add -u``."""
    args = ["add", *files.split()] if files else ["add", "-u"]
    proc = run_git(cwd, *args)
    if proc is None or proc.returncode != 0:
        stderr = proc.stderr.strip() if proc is not None else "git unavailable"
        return CheckResult(
            name="stage",
            status="blocked",
            data={"reason": "git-add-failed", "stderr": stderr},
        )
    return CheckResult(name="stage", status="ok", data={})


def _git_commit(cwd: Path, message: str, expected_branch: str) -> CheckResult:
    """Commit staged changes and return the short SHA.

    Re-asserts the branch after the commit lands (RAISE-11103) — the
    pre-commit ``_assert_branch`` check leaves a TOCTOU window between the
    assertion and this commit where a concurrent checkout in another
    session could land the commit on the wrong branch undetected.
    """
    session_id = resolve_session_id()
    message = with_session_trailer(message, session_id)
    proc = run_git(cwd, "commit", "-m", message)
    if proc is None or proc.returncode != 0:
        # Pre-commit hooks (ruff, black) may modify staged files and exit non-zero,
        # leaving them as 'MM' (staged original + hook-reformatted working tree).
        # Auto-restage those files and retry once — recovers from formatter hooks
        # without requiring agent STOP/manual intervention (RAISE-14916).
        status_proc = run_git(cwd, "status", "--porcelain")
        if status_proc is not None and status_proc.returncode == 0:
            hook_modified = [
                line[3:]
                for line in status_proc.stdout.splitlines()
                if line.startswith("MM")
            ]
            if hook_modified:
                run_git(cwd, "add", *hook_modified)
                proc = run_git(cwd, "commit", "-m", message)
        if proc is None or proc.returncode != 0:
            stderr = proc.stderr.strip() if proc is not None else "git unavailable"
            return CheckResult(
                name="commit",
                status="blocked",
                data={"reason": "commit-failed", "stderr": stderr},
            )
    # Capture short sha
    sha_proc = run_git(cwd, "rev-parse", "--short", "HEAD")
    sha = sha_proc.stdout.strip() if sha_proc and sha_proc.returncode == 0 else ""
    # Post-commit clean-tree assertion (defense-in-depth, D-series guard).
    # Only index-dirty lines (porcelain[0] not in (' ', '?')) are integrity risks:
    # - '??' = untracked (governance docs, temp files) — excluded (RAISE-15007)
    # - ' M' = working-tree-only mod (session bookkeeping files) — excluded (RAISE-14637)
    # - 'M ', 'A ', 'D ', ... = index has staged changes that missed the commit — real risk
    status_proc = run_git(cwd, "status", "--porcelain")
    if status_proc is not None and status_proc.returncode == 0:
        dirty_lines = [
            line
            for line in status_proc.stdout.splitlines()
            if line and line[0] not in (" ", "?")
        ]
        if dirty_lines:
            return CheckResult(
                name="commit",
                status="blocked",
                data={"reason": "dirty-tree-after-commit", "sha": sha},
            )
    # Post-commit branch-drift assertion (RAISE-11103, closes the TOCTOU window)
    branch_ok, current_branch = assert_head_branch(cwd, expected_branch)
    if not branch_ok:
        return CheckResult(
            name="commit",
            status="blocked",
            data={
                "reason": "branch-drift-after-commit",
                "expected": expected_branch,
                "current": current_branch,
                "sha": sha,
            },
        )
    return CheckResult(name="commit", status="ok", data={"sha": sha})


def _emit_signal(work_id: str, task_name: str, cwd: Path | None = None) -> CheckResult:
    """Emit a WorkLifecycle signal — best-effort, never raises (D4)."""
    from raise_cli.telemetry.emit_work import emit_work_lifecycle

    with suppress(Exception):
        emit_work_lifecycle(
            "task",
            work_id,
            "complete",
            "implement",
            task=task_name,
            cwd=str(cwd) if cwd is not None else None,
        )
    return CheckResult(name="signal", status="ok", data={})


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def build_task_complete_report(
    *,
    project_path: Path,
    cwd: Path,
    work_id: str,
    task_name: str,
    expected_branch: str,
    commit_message: str,
    gate_scope: str = "",
    files: str = "",
) -> TaskCompleteReport:
    """Run all steps with block-propagation and return a composite report.

    Steps run in order: gates → branch → stage → commit → signal.
    The first blocked step causes all subsequent steps to be skipped.
    Final ``status`` = worst via STATUS_RANK.

    Args:
        project_path: Project root — used for manifest-driven compliance scope
            expansion (RAISE-8109) and future DB resolution.
        cwd: Working directory for git operations and gate evaluation.
        work_id: Story/bugfix identifier (e.g. "S8370.1").
        task_name: Free-text task name — used in commit message and signal.
        expected_branch: Branch that must be current before any git mutation.
        commit_message: Full commit message (LLM judgment).
        gate_scope: Bare scope path passed to extra_args; "" → full suite.
        files: Space-separated paths to stage; "" → ``git add -u``.
    """
    compliance_scopes = _collect_compliance_scopes(files, project_path)
    changed = files.split() if files else _changed_files(cwd)
    effective_scopes = resolve_effective_scopes(gate_scope, changed)
    blocked = False
    results: list[CheckResult] = []

    def _run_step(name: str, fn: object, *args: object) -> CheckResult:
        nonlocal blocked
        if blocked:
            return _skipped_result(name)
        result: CheckResult = fn(*args)  # type: ignore[operator]
        results.append(result)
        if result.status == "blocked":
            blocked = True
        return result

    def _run_gates_with_compliance() -> CheckResult:
        """Run each effective scope then each compliance scope; return worst result."""
        result: CheckResult | None = None
        for scope in effective_scopes:
            cr = _run_scoped_gates(cwd, scope)
            if cr.status == "blocked":
                return cr
            result = cr
        for scope in compliance_scopes:
            cr = _run_scoped_gates(cwd, scope)
            if cr.status == "blocked":
                return CheckResult(
                    name="gates",
                    status="blocked",
                    data={**cr.data, "compliance_scope": scope},
                )
        return result or CheckResult(name="gates", status="ok", data={})

    gates = _run_step("gates", _run_gates_with_compliance)
    branch = _run_step("branch", _assert_branch, cwd, expected_branch)
    stage = _run_step("stage", _git_stage, cwd, files)
    commit = _run_step("commit", _git_commit, cwd, commit_message, expected_branch)
    signal = _run_step("signal", _emit_signal, work_id, task_name, cwd)

    all_checks = [gates, branch, stage, commit, signal]
    worst = _worst_status(all_checks)

    # Derive top-level clarity fields (RAISE-15493 F1).
    # committed: True only when commit step is ok, carries a sha, and was not
    # skipped.  Anchored on commit.data["sha"] per D2 — never inferred from
    # status alone (a skipped commit returns status="ok" with no sha).
    committed = bool(
        commit.status == "ok"
        and commit.data.get("sha")
        and not commit.data.get("skipped")
    )
    # blocking_gate: first step whose status is "blocked" (pipeline order).
    blocked_step = next((c for c in all_checks if c.status == "blocked"), None)
    blocking_gate: str | None = blocked_step.name if blocked_step else None
    remediation: str | None = _remediation_for(blocked_step) if blocked_step else None

    return TaskCompleteReport(
        status=worst,
        committed=committed,
        blocking_gate=blocking_gate,
        remediation=remediation,
        gates=gates,
        branch=branch,
        stage=stage,
        commit=commit,
        signal=signal,
    )
