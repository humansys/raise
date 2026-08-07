"""ADR-132 capability-overlap fitness function (S14263.2).

``CapabilityOverlapGate`` (ADR-130's tourniquet): flags a NEW public symbol
in a diff that overlaps a registered capability's canonical home, with a
reviewable ``supersedes:``/``duplicate_approved:`` override escape and
``discovery.clone``'s Type-1 exact-clone detector as secondary corroboration
only. Ships in CI with `allow_failure: true` until S14263.4's calibration
gate confirms the FP rate.

Delta semantics (D1, ADR-132 §3a): a symbol is "new" iff its name exists in
HEAD's top-level public symbols but not in the base ref's — never a
HEAD-only scan (that would touch-tax every symbol in a touched file) and
never a `git diff` added-line regex (brittle for multi-line/decorated defs).

S14263.3 (D3, AC7): the git-show/AST delta primitives below are re-pointed
at the shared `gates/drift/_delta.py` (rule-of-three met: capability-overlap
+ P1 `post_refactor_orphan` + P4 `dead_public_api` all need the same
mechanism). Aliased on import so every call site here is unchanged — this
is an import-path-only edit, no behavior change; the pre-existing test
suite is the safety net (D3's own stated acceptance bar).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from raise_cli.discovery.clone import CloneConfig, CloneReport, detect_clones
from raise_cli.gates.capability.registry import CapabilityCard, load_registry
from raise_cli.gates.drift._base import DriftGate
from raise_cli.gates.drift._delta import (
    new_public_symbols_in_file as _new_symbols,
)
from raise_cli.gates.drift._delta import (
    read_at_ref as _read_at_ref,
)
from raise_cli.gates.drift._delta import (
    resolve_merge_base as _resolve_merge_base,
)
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.story.open_service import resolve_dev_branch

_SRC_MARKER = "/src/"
_VERSION_SUFFIX_RE = re.compile(r"(?i)_?v\d+$")


def _module_of_path(path: str) -> str:
    """Derive the dotted module path from a repo-relative source file path.

    Strips the ``packages/<pkg>/src/`` prefix (any package under
    ``packages/*/src/``) and the ``.py`` suffix, replacing path separators
    with dots.

    Example (design Example 4):
        ``packages/raise-cli/src/raise_cli/delivery/fastpath.py``
        -> ``raise_cli.delivery.fastpath``
    """
    normalised = path.replace("\\", "/")
    marker_index = normalised.find(_SRC_MARKER)
    if marker_index != -1:
        normalised = normalised[marker_index + len(_SRC_MARKER) :]
    normalised = normalised.removesuffix(".py")
    return normalised.replace("/", ".")


def _strip_version_suffix(name: str) -> str:
    """Strip a trailing version tag (``_v2``, ``V3``, ...), case-insensitive."""
    return _VERSION_SUFFIX_RE.sub("", name)


def _matches_card(
    new_symbol_name: str, new_module: str, cards: list[CapabilityCard]
) -> CapabilityCard | None:
    """D2 coarse match: foreign module AND (stripped-equality OR substring).

    Deliberately loose wave-1 torniquete (ADR-132) — this threshold is
    exactly what S14263.4 calibration tunes. A symbol in the SAME module as
    the card's canonical home is never foreign (that is the canonical
    implementation itself, not a duplicate).
    """
    candidate = new_symbol_name.lower()
    candidate_stripped = _strip_version_suffix(candidate)
    for card in cards:
        card_module, _, card_symbol = card.canonical_home.partition(":")
        if not card_symbol or card_module == new_module:
            continue
        card_symbol_lower = card_symbol.lower()
        card_symbol_stripped = _strip_version_suffix(card_symbol_lower)
        if card_symbol_stripped == candidate_stripped or card_symbol_lower in candidate:
            return card
    return None


_OVERRIDE_MARKERS = ("supersedes:", "duplicate_approved:")


def _scan_override(symbol_node: ast.AST, source: str) -> str | None:
    """Scan the flagged symbol's OWN span for an override marker (D3, ACN2).

    Scope is deliberately narrow — never the whole file:
    - the comment line immediately preceding the ``def``/``class`` line
      (a standalone comment directly above the statement), and
    - the symbol's own source segment (its header line including any
      trailing comment, its body, and — since it is nested inside the
      segment — its docstring).

    A marker anywhere else in the file (e.g. on a different symbol) is
    invisible to this scan — that is the whole point of per-symbol scoping:
    one symbol's reviewable override must never blanket-suppress another's.
    Returns the matched marker line (for the audit-trail detail), or None.
    """
    lineno = getattr(symbol_node, "lineno", None)
    candidates: list[str] = []
    if lineno is not None:
        lines = source.splitlines()
        preceding_index = lineno - 2  # lineno is 1-indexed; line just above it
        if 0 <= preceding_index < len(lines):
            preceding = lines[preceding_index].strip()
            if preceding.startswith("#"):
                candidates.append(preceding)
    segment = ast.get_source_segment(source, symbol_node)
    if segment is not None:
        candidates.append(segment)

    for text in candidates:
        for marker in _OVERRIDE_MARKERS:
            idx = text.find(marker)
            if idx != -1:
                return text[idx:].splitlines()[0].strip().lstrip("#").strip()
    return None


def _format_violation(symbol: str, module: str, card: CapabilityCard) -> str:
    """Format the AC1 pointer message for a flagged overlap."""
    return (
        f"{symbol} [{module}] overlaps capability {card.id} "
        f"(home: {card.canonical_home}) — reuse it or register "
        "supersedes:/duplicate_approved:<ref>"
    )


def _format_override_audit(
    symbol: str, module: str, card: CapabilityCard, marker: str
) -> str:
    """Format the AC2 audit-trail line for a suppressed overlap."""
    return (
        f"{symbol} [{module}] overlap with capability {card.id} suppressed "
        f"by override: {marker}"
    )


def _package_root(path_str: str, working_dir: Path) -> Path:
    """Return the top-level package dir containing ``path_str`` (D4 bound).

    ``packages/raise-cli/src/raise_cli/delivery/fastpath.py`` ->
    ``<working_dir>/packages/raise-cli/src/raise_cli`` — bounded to the
    flagged file's own distribution package, never the whole monorepo
    (the perf/scope note in D4), while still wide enough to see a sibling
    module elsewhere in the SAME package (e.g. ``raise_cli/memory/sync.py``
    when the flagged file is ``raise_cli/delivery/fastpath.py``).
    """
    normalised = path_str.replace("\\", "/")
    marker_index = normalised.find(_SRC_MARKER)
    if marker_index == -1:
        return working_dir / Path(path_str).parent
    after_src = normalised[marker_index + len(_SRC_MARKER) :]
    top_level = after_src.split("/", 1)[0]
    src_dir = normalised[: marker_index + len(_SRC_MARKER)]
    return working_dir / src_dir / top_level


def _clone_signal(
    flagged_path: str,
    card: CapabilityCard,
    working_dir: Path,
    clone_cache: dict[Path, CloneReport],
) -> str | None:
    """Secondary Type-1 clone corroboration for an ALREADY-flagged overlap (D4).

    Never an independent trigger or suppressor — ``_scan_changed_file`` only
    calls this once a name-collision violation already exists. Bounded to
    the flagged file's own top-level package (``_package_root``), never a
    whole-tree scan. Best-effort: any failure (missing dir, detection
    error) yields ``None`` — a missing corroboration signal never blocks or
    changes the primary violation's outcome.

    ``clone_cache`` is scoped to one ``evaluate()`` call (passed in by the
    caller, never persisted) — several violations landing in the same
    package within one diff reuse the same whole-package clone scan instead
    of re-running ``detect_clones`` per symbol.
    """
    package_root = _package_root(flagged_path, working_dir)
    if not package_root.is_dir():
        return None
    flagged_abs = working_dir / flagged_path
    try:
        flagged_rel = flagged_abs.relative_to(package_root).as_posix()
    except ValueError:
        return None

    card_module, _, _ = card.canonical_home.partition(":")
    card_module_parts = card_module.split(".")
    if card_module_parts and card_module_parts[0] == package_root.name:
        card_module_parts = card_module_parts[1:]
    card_rel_hint = "/".join(card_module_parts) + ".py"

    if package_root in clone_cache:
        report = clone_cache[package_root]
    else:
        try:
            report = detect_clones(package_root, CloneConfig())
        except Exception:  # noqa: BLE001 — corroboration is best-effort, never fatal
            return None
        clone_cache[package_root] = report

    for cluster in report.clones:
        fragment_paths = {f.file_path for f in cluster.fragments}
        if flagged_rel not in fragment_paths:
            continue
        match = next(
            (f for f in cluster.fragments if f.file_path == card_rel_hint), None
        )
        if match is None:
            continue
        return (
            f"Clone signal: {cluster.line_count}-line Type-1 clone with "
            f"{match.file_path}:{match.start_line}-{match.end_line}"
        )
    return None


def _scan_changed_file(
    path_str: str,
    working_dir: Path,
    merge_base: str,
    cards: list[CapabilityCard],
    clone_cache: dict[Path, CloneReport],
) -> tuple[list[str], list[str]]:
    """Return (violations, overrides) for one changed ``.py`` file.

    Isolated from ``evaluate()`` to keep the orchestration method's
    cyclomatic complexity low (KISS) — this holds the whole per-file
    decision: delta -> match -> override-scan.
    """
    abs_path = working_dir / path_str
    if not abs_path.is_file():
        return [], []  # deleted in HEAD — nothing new to check
    try:
        head_src = abs_path.read_text(encoding="utf-8")
        base_src = _read_at_ref(merge_base, path_str, working_dir)
        new_syms = _new_symbols(head_src, base_src)
    except (SyntaxError, UnicodeDecodeError, OSError):
        # A single malformed/non-UTF-8 .py file must not blind the scan for
        # the rest of the diff (best-effort, same philosophy as
        # _read_at_ref/_resolve_merge_base/_clone_signal) — degrade per-file,
        # never whole-gate.
        return [], []
    if not new_syms:
        return [], []

    module = _module_of_path(path_str)
    violations: list[str] = []
    overrides: list[str] = []
    for name, node in new_syms.items():
        card = _matches_card(name, module, cards)
        if card is None:
            continue
        marker = _scan_override(node, head_src)
        if marker is not None:
            overrides.append(_format_override_audit(name, module, card, marker))
            continue
        violation_line = _format_violation(name, module, card)
        signal = _clone_signal(path_str, card, working_dir, clone_cache)
        if signal is not None:
            violation_line = f"{violation_line}\n  {signal}"
        violations.append(violation_line)
    return violations, overrides


class CapabilityOverlapGate(DriftGate):
    """ADR-132 fitness function flagging a NEW public symbol duplicating a capability.

    Real blocker (D5) — ``is_blocker=True`` reflects semantic intent; the
    ``guard:capability-overlap`` CI job (Task 5) wraps it in
    ``allow_failure: true`` at the job level, so a violation surfaces
    (exit 1) without blocking the MR until S14263.4 calibration confirms
    acceptable precision.
    """

    gate_id = "capability-overlap"
    description = "New public symbol overlapping a foreign canonical home (ADR-132)"
    is_blocker = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Flag new public symbols in the diff that collide a foreign capability."""
        cards = load_registry(context.working_dir)
        if not cards:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no capability registry, nothing to check",
            )

        base_branch = resolve_dev_branch(context.working_dir)
        merge_base = _resolve_merge_base(base_branch, context.working_dir)
        if merge_base is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="⚠ SKIPPED (cannot evaluate): base ref unresolvable",
            )

        violations: list[str] = []
        overrides: list[str] = []
        clone_cache: dict[Path, CloneReport] = {}
        for rel_path in context.changed_files or ():
            path_str = rel_path.as_posix()
            if not path_str.endswith(".py"):
                continue
            file_violations, file_overrides = _scan_changed_file(
                path_str, context.working_dir, merge_base, cards, clone_cache
            )
            violations.extend(file_violations)
            overrides.extend(file_overrides)

        if violations:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{len(violations)} capability overlap violation(s)",
                details=tuple(violations) + tuple(overrides),
            )
        if overrides:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{len(overrides)} capability overlap(s) overridden",
                details=tuple(overrides),
            )
        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="no capability overlaps detected",
        )
