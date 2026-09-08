"""Advisory edge derivation from the initiative x component DMM (Layer 2).

Advisory edges are derived in-memory from initiative_profiles — they are NOT
persisted in portfolio_deps. Only human-promoted/declared edges go to the DB
(see storage.py PortfolioStore.promote_to_confirmed / declare_edge).

Design: design.md D1/D3 (RAISE-15198 e15198-portfolio-impact-model).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from raise_cli.portfolio.storage import InitiativeProfile


@dataclass
class AdvisoryEdge:
    """An advisory dependency edge derived from the DMM."""

    source: str  # initiative_key
    target: str  # component_id (impacted_by) or initiative_key (sequence_with)
    type: str  # "impacted_by" | "sequence_with"
    rationale: str = ""


def derive_advisory_edges(profiles: list[InitiativeProfile]) -> list[AdvisoryEdge]:
    """Derive advisory edges from initiative profiles.

    Rules:
    1. impacted_by: for each profile x component_touched
       -> AdvisoryEdge(initiative, component, "impacted_by")
    2. sequence_with: for each pair (A, B) sharing >=1 component, if
       A.change_mode == "breaking" and B.change_mode != "breaking"
       -> AdvisoryEdge(B, A, "sequence_with", "breaking initiative must precede")
       (the non-breaking initiative sequences after the breaking one)
    """
    edges: list[AdvisoryEdge] = []

    for profile in profiles:
        for component in profile.components_touched:
            edges.append(
                AdvisoryEdge(
                    source=profile.initiative_key,
                    target=component,
                    type="impacted_by",
                )
            )

    for a, b in combinations(profiles, 2):
        shared = set(a.components_touched) & set(b.components_touched)
        if not shared:
            continue
        breaking, non_breaking = None, None
        if a.change_mode == "breaking" and b.change_mode != "breaking":
            breaking, non_breaking = a, b
        elif b.change_mode == "breaking" and a.change_mode != "breaking":
            breaking, non_breaking = b, a
        if breaking is not None and non_breaking is not None:
            edges.append(
                AdvisoryEdge(
                    source=non_breaking.initiative_key,
                    target=breaking.initiative_key,
                    type="sequence_with",
                    rationale="breaking initiative must precede",
                )
            )
        # Both breaking: no automatic ordering — a human must resolve via
        # promote_to_confirmed with an explicit rationale.

    return edges
