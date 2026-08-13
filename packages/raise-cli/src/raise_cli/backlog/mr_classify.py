"""MR state classification for unlanded close-drift candidates (RAISE-15880, S15853.5).

S15853.4's ``rai backlog close-drift`` reports UNLANDED candidates —
evidence commit exists but never landed on the development ref — without
distinguishing an MR still in review (informational) from an MR closed
without merging (a real drifted close, worth reverting).

Resolution chain, entirely fail-open (D1-D2, corrected from the epic
design's original premise — see s15853.5-story.md):

1. ``resolve_mr_branch`` (``close_drift.py``) — the remote branch that
   still contains the evidence commit, resolved via git alone. There is
   no persisted MR reference anywhere in Jira to resolve from instead
   (verified live: ``rai-mr-create`` writes its metadata block into the MR
   *description*, never into Jira).
2. ``resolve_mr_number`` — ``glab api`` against that branch. GitLab's REST
   API (unlike ``glab mr list``'s human-readable table) returns clean JSON
   with no repo-id resolution needed — ``:fullpath`` is resolved by glab
   itself from the local git remote.
3. ``classify_mr_state`` — ``glab api`` against the resolved MR number.
   GitLab's raw state is ``opened|merged|closed``; normalized to
   ``open|merged|closed`` to match ``ScmPrResult.state``'s convention.

The ``RaiseServerScmAdapter`` tier the epic design called for is
deliberately not implemented here: ``get_pr`` requires a ``repo_id`` that
nothing in this codebase can resolve automatically (``rai scm get-pr``,
the adapter's only existing consumer, requires it as a manual flag) —
building that resolution would be speculation, not implementation. Recorded
as deferred work, not silently dropped.

Any failure at any step degrades to "drift sin clasificar" (S15853.4's own
established terminal state) rather than raising — this module never
executes a remediation, it only proposes one as text (D4/AC7).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote

from pydantic import BaseModel

from raise_cli.backlog.close_drift import resolve_mr_branch

_GLAB_STATE_MAP: dict[str, str] = {
    "opened": "open",
    "merged": "merged",
    "closed": "closed",
}

_REMEDIATION_LABELS: dict[str, str] = {
    "closed": "revert candidate",
    "open": "informational (MR still open)",
    "merged": "discrepancy — MR merged but evidence commit is not an ancestor",
}


class MrClassification(BaseModel, frozen=True):
    """Tier-2 classification of one UNLANDED close-drift candidate."""

    key: str
    branch: str | None = None
    mr_number: int | None = None
    mr_state: str | None = None
    note: str = ""

    @property
    def remediation_label(self) -> str:
        """Human-readable classification — never an action, only a label."""
        if self.mr_state is not None:
            return _REMEDIATION_LABELS.get(self.mr_state, self.mr_state)
        if self.mr_number is not None:
            return "MR state unavailable"
        return "unclassified"


def _run_glab(
    project_root: Path, *args: str
) -> subprocess.CompletedProcess[str] | None:
    """Run glab and return the completed process, or None if it failed to spawn."""
    try:
        return subprocess.run(  # noqa: S603 — fixed glab executable, controlled args
            ["glab", *args],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return None


def resolve_mr_number(project_root: Path, branch: str) -> int | None:
    """Resolve the MR number for ``branch`` via ``glab api`` (any state).

    Returns None on any failure: glab unavailable, non-zero exit, malformed
    JSON, or zero results — all degrade the same way (no MR resolvable),
    never raise.
    """
    result = _run_glab(
        project_root,
        "api",
        f"projects/:fullpath/merge_requests?source_branch={quote(branch, safe='/')}"
        "&state=all",
    )
    if result is None or result.returncode != 0:
        return None
    try:
        data: Any = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list) or not data:
        return None
    first = data[0]
    if not isinstance(first, dict):
        return None
    iid = first.get("iid")
    return iid if isinstance(iid, int) else None


def classify_mr_state(project_root: Path, mr_number: int) -> str | None:
    """Resolve and normalize the MR's state, or None on any failure.

    GitLab's raw ``opened`` is normalized to ``open`` to match
    ``ScmPrResult.state``'s convention; an unrecognized state also returns
    None rather than surfacing a raw, unclassified value.
    """
    result = _run_glab(
        project_root, "api", f"projects/:fullpath/merge_requests/{mr_number}"
    )
    if result is None or result.returncode != 0:
        return None
    try:
        data: Any = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    raw_state = data.get("state")
    if not isinstance(raw_state, str):
        return None
    return _GLAB_STATE_MAP.get(raw_state)


def classify_candidate(
    project_root: Path, key: str, evidence_sha: str
) -> MrClassification:
    """Classify one UNLANDED candidate through the full fail-open chain.

    Never raises (AC6/AC7): any exception from the glab/git layer is caught
    and degrades to an unclassified result — this is a report-only command,
    never a traceback.
    """
    try:
        branch = resolve_mr_branch(project_root, evidence_sha)
        if branch is None:
            return MrClassification(
                key=key, note="unclassified — no remote branch contains evidence_sha"
            )

        mr_number = resolve_mr_number(project_root, branch)
        if mr_number is None:
            return MrClassification(
                key=key,
                branch=branch,
                note="unclassified — glab found no MR for this branch",
            )

        mr_state = classify_mr_state(project_root, mr_number)
        note = "" if mr_state is not None else "MR state could not be resolved"
        return MrClassification(
            key=key,
            branch=branch,
            mr_number=mr_number,
            mr_state=mr_state,
            note=note,
        )
    except Exception as exc:  # noqa: BLE001 — report-only, never a traceback (AC6/AC7)
        return MrClassification(
            key=key, note=f"unclassified — classification failed: {exc}"
        )
