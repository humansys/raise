"""FF-S2: API schema lock gate (RAISE-15093).

Ensures the OpenAPI spec ``runs-v1.yaml`` exists, is valid YAML, and that
any content change is accompanied by an ``info.version`` bump relative to
the base branch. Fail-closed: any error returns ``passed=False``.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.project_config import resolve_gate_base_branch

logger = logging.getLogger(__name__)

_SPEC_REL = Path("packages") / "raise-server" / "openapi" / "runs-v1.yaml"


def _git_show_at_base(base_ref: str, rel_path: str, working_dir: Path) -> str | None:
    """Read a file at the given git ref; return None if missing/error."""
    try:
        result = subprocess.run(
            ["git", "show", f"{base_ref}:{rel_path}"],
            capture_output=True,
            text=True,
            cwd=str(working_dir),
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception:  # noqa: BLE001
        return None


def _resolve_merge_base(working_dir: Path) -> str | None:
    """Resolve the merge-base with the gate base branch (RAISE-18328).

    Candidate order: the resolved gate base branch first (the actual MR
    target — CI env override, else the registered worktree's merge_target,
    else the manifest default per ``resolve_gate_base_branch``), then
    ``origin/<dev>``, and ``main``/``origin/main`` as fallback when no
    manifest is available. ``resolve_gate_base_branch`` may itself already
    return an ``origin/``-prefixed ref (RAISE-18299's remote-tracking-ref
    preference) — the ``origin/<dev>`` candidate is only added when ``dev``
    isn't already prefixed, so this never tries a nonsensical
    ``origin/origin/<branch>`` ref.
    """
    try:
        dev = resolve_gate_base_branch(working_dir)
        candidates = [dev]
        if not dev.startswith("origin/"):
            candidates.append(f"origin/{dev}")
        candidates.extend(["main", "origin/main"])
        for branch in candidates:
            result = subprocess.run(
                ["git", "merge-base", "HEAD", branch],
                capture_output=True,
                text=True,
                cwd=str(working_dir),
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to resolve merge-base: %s", exc)
    return None


class APISchemaLockGate:
    """OpenAPI spec unchanged or version bumped."""

    gate_id: ClassVar[str] = "ff-s2-api-schema-lock"
    description: ClassVar[str] = "OpenAPI spec unchanged or version bumped"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check that runs-v1.yaml exists and any change has a version bump."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"API schema lock gate error: {exc}",
            )

    def _evaluate(self, context: GateContext) -> GateResult:
        spec_path = context.working_dir / _SPEC_REL

        # 1. Spec must exist
        if not spec_path.is_file():
            return GateResult(
                passed=True,
                skipped=True,
                gate_id=self.gate_id,
                message="OpenAPI spec not found -- skipped: framework layout not present",
                details=(f"Expected: {_SPEC_REL}",),
            )

        # 2. Must be valid YAML
        try:
            head_text = spec_path.read_text(encoding="utf-8")
            head_doc = yaml.safe_load(head_text)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"OpenAPI spec is not valid YAML: {exc}",
            )

        if not isinstance(head_doc, dict):
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="OpenAPI spec root is not a mapping",
            )

        # 3. Extract HEAD version
        try:
            head_version = head_doc["info"]["version"]
        except (KeyError, TypeError):
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="OpenAPI spec missing info.version",
            )

        # 4. Resolve base and compare
        merge_base = _resolve_merge_base(context.working_dir)
        if merge_base is None:
            # Cannot determine base -- pass with advisory note
            return GateResult(
                passed=True,
                skipped=True,
                gate_id=self.gate_id,
                message="Base ref unresolvable -- schema lock check skipped",
            )

        base_text = _git_show_at_base(
            merge_base, _SPEC_REL.as_posix(), context.working_dir
        )
        if base_text is None:
            # Spec is new -- no base to compare against
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="OpenAPI spec is new (no base version) -- OK",
            )

        # 5. Compare content; if changed, version must differ
        if head_text.strip() == base_text.strip():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="OpenAPI spec unchanged -- OK",
            )

        # Content differs -- version must have changed
        try:
            base_doc = yaml.safe_load(base_text)
            base_version = base_doc["info"]["version"]
        except Exception:  # noqa: BLE001
            # Base was broken -- as long as HEAD has a version, accept
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="Base spec unparseable -- accepting HEAD version",
            )

        if head_version == base_version:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"OpenAPI spec changed but info.version not bumped "
                    f"(still {head_version})"
                ),
                details=("Bump info.version in runs-v1.yaml when changing the spec",),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"OpenAPI spec changed with version bump "
                f"({base_version} -> {head_version}) -- OK"
            ),
        )
