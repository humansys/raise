"""Base class for drift detection gates.

All drift gates are advisory (is_blocker=False) until FP calibrated.
Advisory guards return passed=True with violation details in message/details,
and now (RAISE-14280) ``advisory=True`` + a visible WARN log when violations
are found — never a silent pass. See ``gates/drift/baseline.py`` for how
``--strict-drift`` turns violations NOT in the committed baseline into a
hard fail without touching this default (local, non-strict) behavior.

RAISE-15991: the three "cannot evaluate" builders below additionally set
``GateResult.skipped``. A non-verdict is not a pass, and before that field
the distinction existed only in the message prose — invisible to CI, the
HUD, and MCP callers. ``--strict-drift`` blocks on it.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_GRAPH_FILE = "index.json"

_IGNORE_MARKER = "# drift: ignore"
_EXCLUDE_DIRS = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        ".tox",
        "node_modules",
        "dist",
        "build",
        ".mypy_cache",
    }
)
# Any venv-like sibling of the primary .venv (e.g. .venv-mcp, .venv-agent) —
# RAISE-14375: _EXCLUDE_DIRS only matched the exact names ".venv"/"venv", so
# .venv-mcp's site-packages leaked ~39 entries into governance/drift-baseline.json.
_EXCLUDE_DIR_PREFIXES = (".venv-", "venv-")


def is_excluded(path: Path, root: Path) -> bool:
    """Return True if path is inside an excluded directory."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    if _EXCLUDE_DIRS & set(parts):
        return True
    return any(part.startswith(_EXCLUDE_DIR_PREFIXES) for part in parts)


def scoped_rglob(
    root: Path, pattern: str, changed_files: tuple[Path, ...] | None
) -> Iterator[Path]:
    """Yield ``root.rglob(pattern)`` results, intersected with ``changed_files``.

    ``changed_files=None`` preserves the current unscoped behavior (blanket
    sweeps, ``before:epic:close``). When set, only paths whose ``root``-relative
    form is a member of ``changed_files`` are yielded — this is what keeps
    story-close filesystem drift gates from reporting pre-existing drift in
    files the story never touched (RAISE-10933).
    """
    if changed_files is None:
        yield from root.rglob(pattern)
        return
    changed = set(changed_files)
    for path in root.rglob(pattern):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel in changed:
            yield path


def is_file_in_scope(
    file_ref: str | None, changed_files: tuple[Path, ...] | None
) -> bool:
    """Return True if ``file_ref`` (repo-relative) is in ``changed_files``.

    ``changed_files=None`` means unscoped — always in scope. A missing or
    unresolvable ``file_ref`` under an active scope is treated as out of
    scope: precision is the point of scoping, so an unattributable graph
    symbol is not reported as story-caused drift (RAISE-10933).
    """
    if changed_files is None:
        return True
    if not file_ref:
        return False
    return Path(file_ref) in changed_files


def load_graph(working_dir: Path) -> Any | None:
    """Load the knowledge graph via the active backend (RAISE-14279).

    Resolves through ``get_active_backend()`` — the same factory the rest of
    the CLI uses (SQLite Community default, or DualWrite/API when a server is
    configured, see ``raise_cli.graph.backends``) — instead of gating on the
    legacy ``.raise/rai/memory/index.json`` file. That file is a migration
    artifact most SQLite-backed projects never populate, which left every
    graph-drift guard permanently skipped (dead since inception).

    Returns None only when the backend genuinely cannot produce a graph
    (construction/query failure) — a legitimate but rarer case now. Guards
    must render that as a noisy, distinguishable skip (see
    ``graph_unavailable_result``), never a silent pass.
    """
    try:
        from raise_cli.graph.backends import get_active_backend

        graph_path = working_dir / ".raise" / "rai" / "memory" / _GRAPH_FILE
        backend = get_active_backend(graph_path, project_root=working_dir)
        return backend.load()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Graph unavailable: %s", exc)
        return None


def has_ignore_marker(path: Path) -> bool:
    """Return True if the file contains ``# drift: ignore`` on any line."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return _IGNORE_MARKER in text


def graph_unavailable_result(gate_id: str) -> GateResult:
    """Build the noisy, distinguishable skip result for an unresolvable graph.

    RAISE-14279: a skip must never be indistinguishable from a pass in logs
    or the HUD. Logs a visible warning (fail-loud) and returns a message with
    a fixed, greppable prefix distinct from both ``advisory()``'s clean-pass
    message and its violation-summary message.

    RAISE-15991: also sets ``skipped=True``. The greppable message alone was
    prose — a machine (CI, HUD, MCP) saw only ``passed=True`` and could not
    tell "checked, clean" from "never checked". ``passed`` stays True so the
    default remains non-blocking; ``--strict-drift`` opts into failing.
    """
    logger.warning("%s: graph unavailable — advisory drift check skipped", gate_id)
    return GateResult(
        passed=True,
        gate_id=gate_id,
        message="⚠ SKIPPED (cannot evaluate): graph unavailable",
        skipped=True,
    )


def graph_empty_result(gate_id: str) -> GateResult:
    """Build the noisy, distinguishable skip result for a 0-node graph (RAISE-14375).

    A graph that loaded successfully but holds 0 nodes is NOT the same as
    "evaluated the codebase and found no violations" — it means nothing was
    ever indexed for this project in this environment (most commonly: a CI
    runner with no ``RAISE_SERVER_URL``/``RAISE_API_KEY`` and no persisted
    local graph — the CI job never runs ``rai graph build``). Reporting that
    as ``advisory()``'s clean-pass ("No violations") would be a silent-pass
    exactly like the ``graph is None`` case ``graph_unavailable_result``
    already guards against — this is its sibling for the empty-but-not-None
    case. Non-blocking: this is a visible skip, not a hard fail, so a
    graph-less environment does not brick every MR. Carries ``skipped=True``
    (RAISE-15991) so that non-verdict is machine-readable, not prose-only.
    """
    logger.warning("%s: graph empty (0 nodes) — advisory drift check skipped", gate_id)
    return GateResult(
        passed=True,
        gate_id=gate_id,
        message="⚠ SKIPPED (cannot evaluate): graph empty (0 nodes)",
        skipped=True,
    )


def base_unresolvable_result(gate_id: str) -> GateResult:
    """Build the noisy, distinguishable skip result for an unresolvable base ref.

    S14263.3 D4/OQ4: P1/P4's delta filter needs a resolved merge-base to
    decide "newly added." When the base ref can't be resolved (shallow CI
    clone missing the dev branch, a detached checkout, or any git-plumbing
    failure), "newly added" is undecidable — degrading to "all HEAD symbols
    new" would reintroduce the exact stock-on-touch / touch-tax false
    positive RAISE-14568 fixed for. Sibling of ``graph_unavailable_result``/
    ``graph_empty_result``: same ``passed=True`` + ``skipped=True`` + WARN-log
    shape, a distinct greppable message (never "No violations", never the
    graph-skip wording).
    """
    logger.warning(
        "%s: base ref unresolvable — delta undecidable — advisory drift check skipped",
        gate_id,
    )
    return GateResult(
        passed=True,
        gate_id=gate_id,
        message=(
            "⚠ SKIPPED (cannot evaluate): base ref unresolvable — delta undecidable"
        ),
        skipped=True,
    )


def classify_graph(graph: Any | None, gate_id: str) -> GateResult | None:
    """Classify an already-loaded graph so the 4 graph-backed gates share one check.

    Returns ``None`` when the gate should proceed to evaluate ``graph``, or a
    skip ``GateResult`` when it must short-circuit instead — distinguishing
    three states (RAISE-14279 + RAISE-14375):

    - backend construction/query failure -> ``graph is None`` ->
      ``graph_unavailable_result`` ("unavailable", not evaluated at all).
    - backend fine but 0 nodes indexed -> ``graph_empty_result`` ("empty",
      cannot evaluate — most commonly a CI runner that never ran
      ``rai graph build`` and has no ``RAISE_SERVER_URL``/``RAISE_API_KEY``).
    - a real, populated graph -> ``None``, proceed to evaluate.

    Both skip results are non-blocking (``passed=True``) — a graph-less
    environment must never brick every MR. Takes the already-loaded graph
    (rather than ``working_dir``) so each gate keeps calling its own
    module-local ``load_graph`` — preserves the existing
    ``patch("raise_cli.gates.drift.<gate>.load_graph", ...)`` test seam.
    """
    if graph is None:
        return graph_unavailable_result(gate_id)
    if graph.node_count == 0:
        return graph_empty_result(gate_id)
    return None


def advisory(
    gate_id: str, violations: list[str], clean_msg: str = "No violations"
) -> GateResult:
    """Build an advisory GateResult — always passed=True, never silent.

    RAISE-14280 (S14262.5, supersedes PAT-E-1358/1364): a non-empty
    ``violations`` list always logs a visible WARN and always sets
    ``advisory=True`` on the result. ``passed`` stays True by design — no
    drift gate flips to blocking here — but the violations are no longer
    indistinguishable from a clean pass in logs/HUD/CLI render, and
    ``--strict-drift`` (``cli/commands/gate.py`` + ``gates/drift/baseline.py``)
    can now block the subset of these violations that is NOT frozen in the
    committed ``governance/drift-baseline.json``. PAT-E-1358's old semantics
    ("advisory = never visible, never blockable") no longer apply; the
    pattern is reinforced with this new one, not left standing.
    """
    if not violations:
        return GateResult(passed=True, gate_id=gate_id, message=clean_msg)
    summary = f"⚠ DRIFT: {len(violations)} violation(s) found"
    logger.warning("%s: %s", gate_id, summary)
    return GateResult(
        passed=True,
        gate_id=gate_id,
        message=summary,
        details=tuple(violations),
        advisory=True,
    )


class DriftGate:
    """Base for all drift WorkflowGate implementations.

    Subclasses must define ``gate_id``, ``description``, and ``evaluate()``.
    """

    gate_id: ClassVar[str]
    description: ClassVar[str]
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = False

    def evaluate(self, _context: GateContext) -> GateResult:  # pragma: no cover
        raise NotImplementedError

    # Convenience aliases kept on the class for subclass access
    _load_graph = staticmethod(load_graph)
    _has_ignore_marker = staticmethod(has_ignore_marker)
    _is_excluded = staticmethod(is_excluded)
    _advisory = staticmethod(advisory)
    _graph_unavailable = staticmethod(graph_unavailable_result)
    _graph_empty = staticmethod(graph_empty_result)
    _base_unresolvable = staticmethod(base_unresolvable_result)
    _classify_graph = staticmethod(classify_graph)
    _scoped_rglob = staticmethod(scoped_rglob)
    _is_file_in_scope = staticmethod(is_file_in_scope)
