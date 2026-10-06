"""ADR-132 capability registry — schema + loader.

Deliberately mirrors ``raise_cli.gates.drift.baseline:load_baseline``'s
shape (same repo-root ``governance/`` data-file pattern, same
``project_root`` resolution) — DRY reuse of an established convention.

Missing-data contract (D4, ADR-132):
- File ABSENT -> return ``[]`` (gate skips: "no capability registry").
- File PRESENT-BUT-CORRUPT -> propagate ``yaml.YAMLError`` /
  ``pydantic.ValidationError`` uncaught (fail loud — a broken registry
  in RaiSE's own repo must fail the harness, not silently skip).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

REGISTRY_REL_PATH = Path("governance") / "capability-registry.yaml"


class CapabilityCard(BaseModel):
    """A single declared capability: intent, canonical home, and guardrails."""

    id: str
    intent: str
    canonical_home: str  # "module.path:Symbol"
    caller_rule: str
    anti_pattern: str
    decision_ref: str  # required — no traceable decision, no entry
    entry_point_exempt: bool = False


def load_registry(project_root: Path) -> list[CapabilityCard]:
    """Load capability cards from ``<project_root>/governance/capability-registry.yaml``.

    Absent file -> ``[]`` (gate skips: "no capability registry").
    Present-but-corrupt -> propagates yaml/ValidationError (fail loud).
    Mirrors ``gates.drift.baseline:load_baseline(working_dir)``'s path/resolution
    shape only — NOT its error handling. ``load_baseline`` is fail-open on
    corrupt input (catches and returns ``{}``); this loader is deliberately
    fail-loud (see D4 in the story design) since a corrupt registry inside
    RaiSE's own repo should never be silently ignored.
    """
    path = project_root / REGISTRY_REL_PATH
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [CapabilityCard.model_validate(item) for item in raw]
