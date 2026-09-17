"""Drift detection WorkflowGate implementations.

Active guards for ``workflow_point = "before:story:close"`` plus
one advisory gate for ``workflow_point = "before:epic:close"``.
All ship with ``is_blocker = False`` — advisory mode until FP calibrated.

Active guards:
- PostRefactorOrphanGate  (P1) — public symbols with 0 external callers
- DeadPublicApiGate       (P4 + CAND-10) — dead API + __init__ omission
- LinterSuppressionGate   (CAND-03) — noqa: C901 clustering
- EpicCloseGate           (P90) — structural metrics vs baseline at epic close

Retired guards (E14263 S14263.5, RAISE-14696 — source files retained):
- StoryAccretionGate      (CAND-05) — retired, low precision
- ParallelSiblingGate     (CAND-04) — superseded by guard:capability-overlap (S14263.2)
- ImportFanInGate         (CAND-17) — intent migrated to import-linter contract
- AuthorizationFanOutGate (AG1) — intent migrated to import-linter contract

Architecture: E2100 S2100.1/S2100.4, ADR-039
"""

from raise_cli.gates.drift.dead_public_api import DeadPublicApiGate
from raise_cli.gates.drift.epic_close import EpicCloseGate
from raise_cli.gates.drift.linter_suppression import LinterSuppressionGate
from raise_cli.gates.drift.post_refactor_orphan import PostRefactorOrphanGate

__all__ = [
    "PostRefactorOrphanGate",
    "DeadPublicApiGate",
    "LinterSuppressionGate",
    "EpicCloseGate",
]
