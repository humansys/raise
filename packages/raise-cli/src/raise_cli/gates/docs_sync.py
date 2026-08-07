"""DocsSyncGate — verify story governance artifacts are published before close.

Reads the local docs_sync SQLite table (written by CompositeDocTarget on each
successful remote publish). No network calls — offline-safe by design.

Skip conditions (gate passes silently):
  - No docs adapter configured (.raise/docs.yaml / .raise/confluence.yaml absent)
  - Story ID cannot be determined (non-story branch + RAISE_DOCS_SYNC_STORY unset)
  - No governance artifacts found on disk for the story

Architecture: ADR-039 §1 (WorkflowGate Protocol), RAISE-3836 (S20.8)
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

_DOCS_YAML = Path(".raise/docs.yaml")
_CONF_YAML = Path(".raise/confluence.yaml")
_STORY_BRANCH_RE = re.compile(r"story/s(\d+\.\d+)/")
_STORY_ENV = "RAISE_DOCS_SYNC_STORY"
_ARTIFACT_KINDS = ("scope", "retrospective")


def _has_docs_adapter(working_dir: Path) -> bool:
    return (working_dir / _DOCS_YAML).exists() or (working_dir / _CONF_YAML).exists()


def _git_branch(working_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return ""


def _resolve_story_id(working_dir: Path) -> str | None:
    env_val = os.environ.get(_STORY_ENV, "").strip()
    if env_val:
        return env_val
    branch = _git_branch(working_dir)
    m = _STORY_BRANCH_RE.search(branch)
    return m.group(1) if m else None


def _find_artifacts(working_dir: Path, story_id: str) -> list[Path]:
    found: list[Path] = []
    for kind in _ARTIFACT_KINDS:
        matches = list(working_dir.glob(f"work/epics/**/{story_id}-{kind}.md"))
        found.extend(p for p in matches if p.is_file())
    return found


def _load_remote_id(working_dir: Path, local_path: str) -> str | None:
    try:
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        db = get_project_db(working_dir)
        create_all(db)
        pid = get_project_id(working_dir)
        row = db.execute(
            "SELECT remote_id FROM docs_sync WHERE local_path = ? AND project_id = ?",
            (local_path, pid),
        ).fetchone()
        db.close()
        return row[0] if row and row[0] else None
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None


class DocsSyncGate:
    """Quality gate: story governance artifacts published to remote docs.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Override story detection: set ``RAISE_DOCS_SYNC_STORY=sN.M`` (useful for
    CI or non-standard branch names).
    """

    gate_id: ClassVar[str] = "gate-docs-sync"
    description: ClassVar[str] = "Story artifacts published to remote docs"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:  # noqa: D102
        wd = context.working_dir

        if not _has_docs_adapter(wd):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no docs adapter configured — skipped",
            )

        story_id = _resolve_story_id(wd)
        if not story_id:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"story ID not determined — skipped "
                    f"(set {_STORY_ENV}=sN.M to override)"
                ),
            )

        artifacts = _find_artifacts(wd, story_id)
        if not artifacts:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"no artifacts found for {story_id} — skipped",
            )

        unpublished: list[str] = []
        for artifact in artifacts:
            remote_id = _load_remote_id(wd, str(artifact))
            if not remote_id:
                unpublished.append(str(artifact.relative_to(wd)))

        if not unpublished:
            count = len(artifacts)
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{count} artifact(s) verified in remote docs",
            )

        details = (
            *[f"{p} — not in docs_sync" for p in unpublished],
            "Publish with: rai docs publish <type> --file <path>",
            f"Then re-run: rai gate check {self.gate_id}",
        )
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=f"{len(unpublished)} artifact(s) not published to remote docs",
            details=details,
        )
