"""Unified gate-execution seam (RAISE-13749 / RAISE-14112 S1).

Single implementation of discovery, ``GateContext`` construction (workflow_point
+ changed_files scoping), exception isolation, and result aggregation. Before
this module existed, four call-sites (CLI ``rai gate check``, GateBridgeHook,
MCP ``raise_gate_check``, task-complete's ``_run_scoped_gates``) each built
this independently and diverged — see ``work/bugs/RAISE-13749/analysis.md``.

Architecture: ADR-039 (WorkflowGate Protocol), RAISE-10933 (story-close
changed_files scoping), RAISE-10440/E10436 (task-complete scope derivation).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.protocol import WorkflowGate
from raise_cli.impact.git_diff import collect_changed_files
from raise_cli.project_config import resolve_dev_branch
from raise_cli.telemetry.audit import emit_gate_report

if TYPE_CHECKING:
    from raise_cli.gates.registry import GateRegistry
    from raise_core.workflow.models import PhaseDefinition

logger = logging.getLogger(__name__)

#: Points whose run is scoped by default to the diff vs merge-target.
#: before:story:close was already scoped (RAISE-10933); the bug-close points
#: are the RAISE-13749/RAISE-15567 fixes — both its precondition and
#: post-transition verification ignore foreign in-flight debt.
SCOPED_POINTS: frozenset[str] = frozenset(
    {"before:story:close", "before:bug:close", "after:bug:close"}
)


class GateNotFoundError(LookupError):
    """Raised by ``run_gate`` when ``gate_id`` is not registered."""


@dataclass(frozen=True)
class GateSkip:
    """An explicit, never-silent skip recorded in a ``GatePointReport``."""

    gate_id: str
    reason: str  # "not-registered" | "no-gates-for-point"


@dataclass(frozen=True)
class ScopeInfo:
    """Provenance of a run's ``changed_files`` scoping decision — never silent.

    ``source`` is one of: ``"explicit"`` (caller-supplied override),
    ``"derived:<base_ref>"`` (resolved from the diff vs merge-target),
    ``"unscoped:blanket"`` (a full sweep — ``run_all_gates``/``run_gate_set``),
    ``"unscoped:point-not-scoped"`` (workflow_point not in ``SCOPED_POINTS``),
    ``"unscoped:derivation-failed"`` (resolution raised — fail-safe, RAISE-10933).
    """

    changed_files: tuple[Path, ...] | None  # None = unscoped
    source: str


@dataclass(frozen=True)
class GatePointReport:
    """Aggregated result of running gates for a workflow point or gate set."""

    workflow_point: str | None  # None = blanket sweep / fixed gate set
    working_dir: Path
    scope: ScopeInfo
    results: tuple[GateResult, ...]
    skips: tuple[GateSkip, ...]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def failures(self) -> tuple[GateResult, ...]:
        """Results that did not pass."""
        return tuple(r for r in self.results if not r.passed)

    @property
    def passed(self) -> tuple[GateResult, ...]:
        """Results that passed."""
        return tuple(r for r in self.results if r.passed)

    @property
    def ok(self) -> bool:
        """True when nothing in ``results`` failed."""
        return not self.failures


def _emit_gate_report_safe(
    report: GatePointReport,
    *,
    issue_id: str | None,
    session_id: str | None = None,
) -> None:
    """Governance audit choke point (RAISE-16691, SD3a) — never affects the caller.

    Belt-and-suspenders around ``emit_gate_report`` (itself already fail-open):
    the call site swallows exceptions too, so a raising emitter can never
    change the report a caller already computed and is about to return.
    """
    try:
        emit_gate_report(report, issue_id=issue_id, session_id=session_id)
    except Exception:  # noqa: BLE001 — fail-open by design (SD3)
        logger.debug(
            "governance audit emission failed at gate choke point", exc_info=True
        )


def _evaluate_isolated(gate: WorkflowGate, context: GateContext) -> GateResult:
    """Run a single gate with exception isolation.

    Gate exceptions are caught and converted to a failed ``GateResult`` —
    gates never crash the caller (parity with the isolation previously
    triplicated in ``gate.py``, ``gate_bridge.py``, ``mcp_tools_gate.py``,
    ``complete_service.py``).
    """
    try:
        return gate.evaluate(context)
    except Exception as exc:  # noqa: BLE001 — isolate gate exceptions
        msg = f"{type(exc).__name__}: {exc}"
        logger.warning("Gate '%s' raised: %s", context.gate_id, msg)
        return GateResult(passed=False, gate_id=context.gate_id, message=msg)


def _derive_changed_files(working_dir: Path, workflow_point: str | None) -> ScopeInfo:
    """Generalization of the former ``gate.py:_resolve_changed_files`` (RAISE-10933).

    Scopes to the diff vs merge-target for any point in ``SCOPED_POINTS``;
    degrades to unscoped (never blocks) on any resolution failure — the
    fallback is recorded in the returned ``ScopeInfo``, never only logged.
    """
    if workflow_point not in SCOPED_POINTS:
        return ScopeInfo(changed_files=None, source="unscoped:point-not-scoped")
    try:
        base_ref = resolve_dev_branch(working_dir)
        changed = collect_changed_files(
            base_ref=base_ref, head_ref=None, cwd=working_dir
        )
        return ScopeInfo(changed_files=tuple(changed), source=f"derived:{base_ref}")
    except Exception as exc:  # noqa: BLE001 — fail-safe unscoped (RAISE-10933 parity)
        # RAISE-14375: a single-line summary (type + message), not exc_info=True —
        # a shallow-clone CI runner missing the base ref hits this constantly
        # (e.g. GitDiffError: unknown revision 'release/3.1.0'), and a raw
        # traceback dump on every such run is noise, not signal. The fallback
        # itself (never block, always degrade to unscoped) is unchanged.
        logger.warning(
            "changed_files scoping unavailable for %s (%s: %s) — falling back "
            "to unscoped",
            workflow_point,
            type(exc).__name__,
            exc,
        )
        return ScopeInfo(changed_files=None, source="unscoped:derivation-failed")


def _resolve_scope(
    working_dir: Path,
    workflow_point: str | None,
    changed_files: Sequence[Path] | None,
) -> ScopeInfo:
    """Explicit override always wins; otherwise derive per ``SCOPED_POINTS``."""
    if changed_files is not None:
        return ScopeInfo(changed_files=tuple(changed_files), source="explicit")
    return _derive_changed_files(working_dir, workflow_point)


def run_gates_for_point(
    workflow_point: str,
    working_dir: Path,
    *,
    changed_files: Sequence[Path] | None = None,
    extra_args: tuple[str, ...] = (),
    session_id: str | None = None,
    issue_id: str | None = None,
    registry: GateRegistry | None = None,
) -> GatePointReport:
    """Run every gate registered for ``workflow_point`` and aggregate a report.

    ``changed_files`` is an explicit override (S3's engine will pass the run's
    own diff here); absent that, scoping follows ``SCOPED_POINTS``. When
    ``registry`` is omitted, a fresh ``GateRegistry`` is discovered — the
    import is function-local so tests can patch
    ``raise_cli.gates.registry.GateRegistry`` and have it apply at call time.

    ``session_id`` (RAISE-12207) is threaded onto each ``GateContext`` so
    session-scoped gates resolve the caller's session even when this runs in a
    process whose env is not the agent's (the in-process MCP emit site).
    """
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()

    gates = registry.get_gates_for_point(workflow_point)
    scope = _resolve_scope(working_dir, workflow_point, changed_files)

    if not gates:
        empty_report = GatePointReport(
            workflow_point=workflow_point,
            working_dir=working_dir,
            scope=scope,
            results=(),
            skips=(
                GateSkip(
                    gate_id=f"(point:{workflow_point})",
                    reason="no-gates-for-point",
                ),
            ),
        )
        _emit_gate_report_safe(empty_report, issue_id=issue_id, session_id=session_id)
        return empty_report

    results = tuple(
        _evaluate_isolated(
            gate,
            GateContext(
                gate_id=gate.gate_id,
                working_dir=working_dir,
                extra_args=extra_args,
                workflow_point=workflow_point,
                changed_files=scope.changed_files,
                session_id=session_id,
                issue_id=issue_id,
            ),
        )
        for gate in gates
    )
    report = GatePointReport(
        workflow_point=workflow_point,
        working_dir=working_dir,
        scope=scope,
        results=results,
        skips=(),
    )
    _emit_gate_report_safe(report, issue_id=issue_id, session_id=session_id)
    return report


def run_all_gates(
    working_dir: Path,
    *,
    extra_args: tuple[str, ...] = (),
    registry: GateRegistry | None = None,
) -> GatePointReport:
    """Blanket sweep — exact ``rai gate check --all`` parity.

    Always ``workflow_point=None`` and unscoped ``changed_files=None``,
    regardless of any gate's own ``workflow_point`` (H1 — ``--all`` stays the
    full-repo diagnostic sweep; ``rai-mr-create``'s backstop depends on this).

    Runs a holistic preflight before any gate: if any app declares an executable
    that is absent from PATH, the sweep fails immediately with actionable
    recovery commands instead of running the long suite (RAISE-17041).
    """
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()

    # Holistic preflight: catch missing executables across all command types
    # before the long test/type/lint/format suite begins (RAISE-17041).
    from raise_cli.gates.builtin._runner import check_app_executables
    from raise_cli.project_config.manifest import load_manifest

    manifest = load_manifest(working_dir)
    if manifest is not None and manifest.project.apps:
        preflight = check_app_executables(manifest.project.apps)
        if preflight is not None:
            preflight_report = GatePointReport(
                workflow_point=None,
                working_dir=working_dir,
                scope=ScopeInfo(changed_files=None, source="unscoped:blanket"),
                results=(preflight,),
                skips=(),
            )
            _emit_gate_report_safe(preflight_report, issue_id=None)
            return preflight_report

    results = tuple(
        _evaluate_isolated(
            gate,
            GateContext(
                gate_id=gate.gate_id,
                working_dir=working_dir,
                extra_args=extra_args,
                workflow_point=None,
                changed_files=None,
            ),
        )
        for gate in registry.gates
    )
    report = GatePointReport(
        workflow_point=None,
        working_dir=working_dir,
        scope=ScopeInfo(changed_files=None, source="unscoped:blanket"),
        results=results,
        skips=(),
    )
    _emit_gate_report_safe(report, issue_id=None)
    return report


def run_gate(
    gate_id: str,
    working_dir: Path,
    *,
    extra_args: tuple[str, ...] = (),
    registry: GateRegistry | None = None,
) -> GateResult:
    """Run a single gate by id — raises ``GateNotFoundError`` if unregistered.

    Context always carries ``workflow_point=gate.workflow_point`` and derives
    ``changed_files`` when that point is in ``SCOPED_POINTS`` (parity with the
    former CLI ``_check_single``).
    """
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()

    gate = registry.get_gate(gate_id)
    if gate is None:
        raise GateNotFoundError(gate_id)

    # getattr, not gate.workflow_point — some test doubles (test_mcp_gate_cwd.py,
    # test_mcp_gate_scope.py) are duck-typed with only gate_id/evaluate and don't
    # carry workflow_point; a hard attribute access would raise outside the
    # exception-isolation this function is supposed to provide.
    gate_workflow_point: str | None = getattr(gate, "workflow_point", None)
    scope = _resolve_scope(working_dir, gate_workflow_point, None)
    context = GateContext(
        gate_id=gate_id,
        working_dir=working_dir,
        extra_args=extra_args,
        workflow_point=gate_workflow_point,
        changed_files=scope.changed_files,
    )
    result = _evaluate_isolated(gate, context)
    report = GatePointReport(
        workflow_point=gate_workflow_point,
        working_dir=working_dir,
        scope=scope,
        results=(result,),
        skips=(),
    )
    _emit_gate_report_safe(report, issue_id=None)
    return result


def run_gates_by_id(
    gate_ids: list[str],
    working_dir: Path,
    *,
    session_id: str | None = None,
    extra_args: tuple[str, ...] = (),
    registry: GateRegistry | None = None,
) -> list[GateResult]:
    """Run gates by declarative id list; fails closed on unknown ids.

    Used by pipeline phases with ``quality_gates`` (RAISE-14934 T2).
    Unlike ``run_gate_set``, an unknown id raises ``PipelineError`` immediately
    rather than recording a silent skip — declarative gates must be fail-closed.
    ``workflow_point`` is set from the gate's own ClassVar so context-aware
    gates (AR gate) enforce rather than skip.

    NOTE (RAISE-16254): quality_gates is an unused extension seam — 0/15
    canonical pipelines declare it. Superseded by ``raise_task_complete``
    which runs gates per-task with package scope (more granular, server-side).
    Kept as-is; do not build new features on this path.
    """
    if not gate_ids:
        return []
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()
    results: list[GateResult] = []
    for gate_id in gate_ids:
        gate = registry.get_gate(gate_id)
        if gate is None:
            from raise_cli.pipeline.loader import PipelineError

            raise PipelineError(
                f"unknown gate id {gate_id!r} in quality_gates — "
                f"run 'rai gate list' to see registered gates"
            )
        gate_wp: str | None = getattr(gate, "workflow_point", None)
        scope = _resolve_scope(working_dir, gate_wp, None)
        context = GateContext(
            gate_id=gate_id,
            working_dir=working_dir,
            extra_args=extra_args,
            workflow_point=gate_wp,
            changed_files=scope.changed_files,
            session_id=session_id,
        )
        results.append(_evaluate_isolated(gate, context))

    if results:
        report = GatePointReport(
            workflow_point=None,
            working_dir=working_dir,
            scope=ScopeInfo(changed_files=None, source="unscoped:blanket"),
            results=tuple(results),
            skips=(),
        )
        _emit_gate_report_safe(report, issue_id=None, session_id=session_id)
    return results


def blocking_failures(
    results: list[GateResult],
    gate_mode: Literal["blocking", "advisory"],
) -> list[GateResult]:
    """Classify gate results as blocking given the phase's gate_mode.

    Used by the pipeline engine (T5) to decide whether to abort after
    ``run_gates_by_id()``. Advisory mode demotes every failure to a
    non-blocking warning; blocking mode (default) surfaces ``passed=False``
    results as abort-worthy.
    """
    if gate_mode == "advisory":
        return []
    return [r for r in results if not r.passed]


def validate_quality_gate_ids(
    phases: Sequence[PhaseDefinition],
    registry: GateRegistry | None = None,
) -> None:
    """Validate all quality_gates IDs in phases are registered; fail-closed.

    Called at pipeline_start before any phase executes (RAISE-14934 T4).
    Reports ALL unknown IDs in one ``PipelineError`` — no silent partial
    acceptance. No-op when no phase declares quality_gates.

    NOTE (RAISE-16254): see ``run_gates_by_id`` — quality_gates is unused,
    superseded by ``raise_task_complete``.
    """
    all_ids = [gid for phase in phases for gid in phase.quality_gates]
    if not all_ids:
        return
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()
    unknown = [gid for gid in all_ids if registry.get_gate(gid) is None]
    if unknown:
        from raise_cli.pipeline.loader import PipelineError

        ids_str = ", ".join(repr(g) for g in unknown)
        raise PipelineError(
            f"unknown gate id(s) in quality_gates: {ids_str} — "
            f"run 'rai gate list' to see registered gates"
        )


def run_gate_set(
    specs: Sequence[tuple[str, tuple[str, ...]]],
    working_dir: Path,
    *,
    registry: GateRegistry | None = None,
) -> GatePointReport:
    """Run a fixed list of ``(gate_id, extra_args)`` specs (for task-complete).

    An unregistered ``gate_id`` yields an explicit ``GateSkip`` in the report
    instead of vanishing silently (the direct fix for the ``continue`` at the
    former ``complete_service.py:_run_scoped_gates``).
    """
    if registry is None:
        from raise_cli.gates.registry import GateRegistry

        registry = GateRegistry()
        registry.discover()

    results: list[GateResult] = []
    skips: list[GateSkip] = []
    for gate_id, gate_extra_args in specs:
        gate = registry.get_gate(gate_id)
        if gate is None:
            skips.append(GateSkip(gate_id=gate_id, reason="not-registered"))
            continue
        context = GateContext(
            gate_id=gate_id,
            working_dir=working_dir,
            extra_args=gate_extra_args,
        )
        results.append(_evaluate_isolated(gate, context))

    report = GatePointReport(
        workflow_point=None,
        working_dir=working_dir,
        scope=ScopeInfo(changed_files=None, source="unscoped:blanket"),
        results=tuple(results),
        skips=tuple(skips),
    )
    _emit_gate_report_safe(report, issue_id=None)
    return report


# ---------------------------------------------------------------------------
# Scope-derive (moved from task/complete_service.py — RAISE-10440/E10436, T7)
#
# Re-export compat (RAISE-13749 T7) — repoint tests and retire the
# complete_service shim in S3/S7 cleanup once no external caller depends on
# the old import path.
# ---------------------------------------------------------------------------

# A changed file under packages/<pkg>/src/... or packages/<pkg>/tests/... maps
# to that package's tests dir (RAISE-10440 / E10436 S3). Travels with
# derive_test_scopes (its only user) to avoid a circular import with
# complete_service.py (AR RAISE-13749 C1).
_PACKAGE_SRC_RE = re.compile(r"^(packages/[^/]+)/(?:src|tests)/")


def derive_test_scopes(files: Sequence[str]) -> list[str]:
    """Map changed files to the package test dirs that cover them (E10436 S3).

    ``packages/<pkg>/src/...``   → ``packages/<pkg>/tests/``
    ``packages/<pkg>/tests/...`` → ``packages/<pkg>/tests/``

    Package-level (not file-level) granularity is the conservative MVP: it runs
    more than strictly necessary but never fewer, so a sibling test that imports
    the changed module still runs. Finer file-level selection is test-impact
    analysis (S6). Paths outside ``packages/<pkg>/{src,tests}/`` are ignored —
    the full suite at MR/CI is the backstop for those. Returns a de-duplicated,
    sorted list of bare scope paths.
    """
    scopes: set[str] = set()
    for f in files:
        m = _PACKAGE_SRC_RE.match(f)
        if m:
            scopes.add(f"{m.group(1)}/tests/")
    return sorted(scopes)


def resolve_effective_scopes(gate_scope: str, changed: Sequence[str]) -> list[str]:
    """Decide which scope(s) the task gates run against (E10436 S3, inverts C1).

    An explicit ``gate_scope`` always wins. Otherwise derive scopes from the
    change set; if nothing maps to a package (or there are no changes), fall back
    to ``[""]`` — the full suite — so an unrecognized change is never silently
    narrowed into a false green.
    """
    if gate_scope:
        return [gate_scope]
    derived = derive_test_scopes(changed)
    return derived if derived else [""]


def types_scope_for(gate_scope: str) -> str:
    """Map a (test) scope to the package ``src`` dir for type-checking.

    gate-types type-checks ``src``, never ``tests`` — the project
    ``type_check_command`` targets ``src`` dirs only and pyright's config
    excludes tests. Appending a bare tests-dir scope to the pyright command
    makes it type-check test files the project intentionally excludes, raising
    pre-existing test-code errors (private usage, untyped fixtures) as false
    blocks (S8370.3 dogfood finding). ``packages/X/tests/...`` → ``packages/X/src``;
    a non-test scope (or empty) is passed through unchanged.
    """
    marker = "/tests"
    idx = gate_scope.find(marker)
    if idx == -1:
        return gate_scope
    return gate_scope[:idx] + "/src"
