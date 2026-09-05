"""ArchitectureDocsFreshGate — gate-docs-architecture-fresh (D-S4, AC6).

Read-only, LLM-free staleness gate: for every module doc under
``governance/architecture/modules/`` carrying a ``rai:auto`` region,
recompute the bundle fingerprint and compare to the region's stored
``src``. Stale -> fail with an actionable "run /rai-docs-update".

**This gate never generates.** It reports staleness and stops — auto-commit
is confined to content a human approved in the same ``/rai-docs-update``
run (D-S4); an unattended pipeline that both synthesizes and commits would
bypass the ADR-025 HITL gate the epic explicitly forbids bypassing.

Skip conditions (gate passes silently), mirroring ``DocsSyncGate``'s own
fail-open shape: no ``governance/architecture/`` tree, no module docs, or
no ``rai:auto`` regions present yet — the pre-first-run state must not
fail every repo that installs RaiSE.

Pure hash comparison: no API key, no network, no node runtime,
milliseconds.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from raise_cli.docs.architecture.bundle import (
    ModuleNotFoundInGraphError,
    build_bundle,
    load_graph,
)
from raise_cli.docs.architecture.fingerprint import fingerprint
from raise_cli.docs.architecture.module_id import module_id_for_doc
from raise_cli.docs.architecture.regions import OrphanMarkerError, parse_regions
from raise_cli.gates.models import GateContext, GateResult

_MODULES_DIR = Path("governance") / "architecture" / "modules"


class ArchitectureDocsFreshGate:
    """Quality gate: generated architecture doc regions are not stale.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.
    """

    gate_id: ClassVar[str] = "gate-docs-architecture-fresh"
    description: ClassVar[str] = "Generated architecture doc regions are not stale"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:  # noqa: D102
        modules_dir = context.working_dir / _MODULES_DIR
        if not modules_dir.is_dir():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"no {_MODULES_DIR} — skipped",
            )

        docs = sorted(modules_dir.glob("*.md"))
        if not docs:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no module docs found — skipped",
            )

        stale: list[str] = []
        checked = 0

        # Hoisted once for the whole evaluation (R9): a full index load per
        # region does not scale to the 25 docs RAISE-15887/15888/15889 add.
        # `project_root=context.working_dir` (R3) keeps graph resolution
        # scoped to the same root as the docs above — otherwise, in a
        # multi-worktree setup where the gate's working_dir differs from
        # process CWD, backend resolution would silently fall back to CWD
        # and cross-wire this repo's docs against a different repo's graph.
        graph = load_graph(project_root=context.working_dir)

        for doc_path in docs:
            text = doc_path.read_text(encoding="utf-8")
            try:
                regions = parse_regions(text)
            except OrphanMarkerError as exc:
                # Count this doc toward `checked` even though no region
                # loop runs for it — otherwise a doc whose ONLY finding is
                # an orphan marker leaves `checked == 0` and gets masked
                # by the skip branch below, silently hiding the orphan
                # (C2 — ADR-146 names orphan markers its principal named
                # failure mode; they must fail loudly, never skip).
                checked += 1
                stale.append(f"{doc_path.name} — orphan marker: {exc}")
                continue

            # RAISE-16033 C1: read the doc's own package: frontmatter
            # (same rule discovery and the curated sidecar loader use)
            # instead of the bare filename stem — otherwise a package-
            # qualified module's id never matches the graph and this
            # gate fail-open-skips every such doc without checking
            # anything.
            module_id = module_id_for_doc(doc_path)
            for region in regions:
                checked += 1
                try:
                    bundle = build_bundle(module_id, graph=graph)
                except ModuleNotFoundInGraphError:
                    # No graph built yet, or module removed — not this
                    # gate's job to fail the build over (fail-open, D-S4).
                    continue
                computed_src = fingerprint(bundle)
                if computed_src != region.src:
                    stale.append(
                        f"{doc_path.name}#{region.id} "
                        f"src {region.src} -> {computed_src} (graph changed)"
                    )

        if checked == 0:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no rai:auto regions found — skipped",
            )

        if not stale:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{checked} region(s) fresh",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=f"{len(stale)} doc(s) stale",
            details=(*stale, "Regenerate with: /rai-docs-update"),
        )
