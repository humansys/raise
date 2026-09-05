"""DomainModelRatifiedGate — guardrail for rai graph assign-bcs (RAISE-16791).

Validates that ``domain-model.yaml`` exists and carries architect sign-off
before allowing BC assignment to proceed.  Without this gate, assign-bcs
contaminates the graph with classifications anchored to unratified or
provisional Bounded Context names.

Checks (ordered, first failure wins):
1. File exists (canonical ``.raise/domain-model.yaml`` or legacy path).
2. ``ratified_by`` is a non-empty string.
3. ``ratified_at`` is present and parseable as a YYYY-MM-DD ISO date.
4. ``bounded_contexts`` has at least one entry.

Architecture: ADR-039 (WorkflowGate Protocol).
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

# Path constants mirrored from raise_cli.ddd.domain_model — not imported from
# there because domain_model.py has a local `from raise_cli.cli.error_handler`
# import inside load_domain_model(), which the 5-layer import linter (RAISE-16340)
# treats as a transitive cli dependency from the gates layer.
_CANONICAL_REL = ".raise/domain-model.yaml"
_LEGACY_REL = "governance/architecture/domain-model.yaml"

_GATE_ID = "gate-domain-model-ratified"


def _resolve_domain_model_path(project_root: Path) -> Path:
    """Resolve domain-model.yaml without importing raise_cli.ddd.domain_model.

    Resolution order mirrors ``get_domain_model_path()`` in domain_model.py:
    1. ``<root>/.raise/domain-model.yaml`` (canonical)
    2. ``<root>/governance/architecture/domain-model.yaml`` (legacy)
    3. Canonical (non-existent default) so callers get a consistent path.
    """
    canonical = project_root / _CANONICAL_REL
    if canonical.exists():
        return canonical
    legacy = project_root / _LEGACY_REL
    if legacy.exists():
        logger.debug("domain-model.yaml found at legacy path %s", legacy)
        return legacy
    return canonical


class DomainModelRatifiedGate:
    """Gate: domain-model.yaml exists and has architect sign-off.

    Registered via the ``rai.gates`` entry point (``domain-model-ratified``).
    Wired into ``rai graph assign-bcs`` as a pre-flight check so that LLM BC
    assignment never proceeds against an unratified model.
    """

    gate_id: ClassVar[str] = _GATE_ID
    description: ClassVar[str] = (
        "domain-model.yaml exists and has architect sign-off "
        "(ratified_by + ratified_at + at least one BC)"
    )
    workflow_point: ClassVar[str] = "pre-assign-bcs"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check domain-model.yaml for architect ratification.

        Args:
            context: Gate evaluation context.  ``context.working_dir`` is used
                as the project root for path resolution.

        Returns:
            :class:`~raise_cli.gates.models.GateResult` — ``passed=True`` when
            all checks succeed, ``passed=False`` with an actionable message on
            the first failure.
        """
        project_root: Path = context.working_dir

        # ------------------------------------------------------------------
        # Check 1: file exists
        # ------------------------------------------------------------------
        dm_path = _resolve_domain_model_path(project_root)
        if not dm_path.exists():
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message=f"domain-model.yaml not found at {dm_path}",
                details=(
                    "Run 'rai ddd discover' to generate .raise/domain-model.yaml",
                    "Then add 'ratified_by' and 'ratified_at' fields before running assign-bcs",
                ),
            )

        # ------------------------------------------------------------------
        # Parse YAML
        # ------------------------------------------------------------------
        try:
            raw = dm_path.read_text(encoding="utf-8")
            data: object = yaml.safe_load(raw)
        except (OSError, yaml.YAMLError) as exc:
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message=f"Failed to read/parse domain-model.yaml: {exc}",
                details=("Fix the YAML syntax in domain-model.yaml",),
            )

        if not isinstance(data, dict):
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message="domain-model.yaml is not a valid YAML mapping",
                details=("Ensure the top-level structure is a YAML object/dict",),
            )

        # ------------------------------------------------------------------
        # Check 2: ratified_by non-empty
        # ------------------------------------------------------------------
        ratified_by = data.get("ratified_by", "")
        if not isinstance(ratified_by, str) or not ratified_by.strip():
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message="domain-model.yaml is missing architect sign-off (ratified_by)",
                details=(
                    "Add 'ratified_by: <architect-email>' to domain-model.yaml",
                    "Example: ratified_by: emilio@humansys.ai",
                ),
            )

        # ------------------------------------------------------------------
        # Check 3: ratified_at valid ISO date (YYYY-MM-DD only)
        # ------------------------------------------------------------------
        ratified_at_raw = data.get("ratified_at", "")
        ratified_at_str = str(ratified_at_raw).strip() if ratified_at_raw else ""

        if not ratified_at_str:
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message="domain-model.yaml is missing ratified_at date",
                details=(
                    "Add 'ratified_at: YYYY-MM-DD' to domain-model.yaml",
                    "Example: ratified_at: 2026-08-31",
                ),
            )

        # Must be exactly a date (YYYY-MM-DD) — not a datetime, not a free string
        # datetime ISO strings contain 'T' or more than 10 chars in date portion
        if not _is_valid_iso_date_only(ratified_at_str):
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message=f"ratified_at value '{ratified_at_str}' is not a valid ISO date (YYYY-MM-DD)",
                details=(
                    "Use YYYY-MM-DD format for ratified_at",
                    "Example: ratified_at: 2026-08-31",
                ),
            )

        # ------------------------------------------------------------------
        # Check 4: at least one bounded_context
        # ------------------------------------------------------------------
        bounded_contexts = data.get("bounded_contexts")
        if not isinstance(bounded_contexts, list) or len(bounded_contexts) == 0:
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message="domain-model.yaml has no bounded_contexts defined",
                details=(
                    "Add at least one bounded context before running assign-bcs",
                    "Example: bounded_contexts:\n  - name: governance\n    description: Governance BC",
                ),
            )

        # All checks passed
        bc_count = len(bounded_contexts)
        return GateResult(
            passed=True,
            gate_id=_GATE_ID,
            message=(
                f"domain-model.yaml ratified by '{ratified_by}' on {ratified_at_str} "
                f"({bc_count} bounded context{'s' if bc_count != 1 else ''})"
            ),
        )


def _is_valid_iso_date_only(value: str) -> bool:
    """Return True iff *value* is a strict YYYY-MM-DD ISO date string.

    Rejects datetime strings (containing 'T'), freeform text, and partial dates.
    """
    # Fast reject: must be exactly 10 characters and contain no 'T'
    if len(value) != 10 or "T" in value:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False
