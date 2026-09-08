"""Shared Initiative issue-key resolution for point-bound governance gates.

``GateContext`` (``gates/models.py``) carries no ``issue_id`` field by
design — every point-bound gate resolves its own subject. The
``before:bug:close`` precedent (``close_sync_gate.py``) resolves the issue
key via a git-branch regex against ``context.working_dir``. Both
``StrategicFitGate`` and ``ChildEpicsCompleteGate`` need the exact same
resolution for the Initiative pipeline (``execution.branch_pattern:
"initiative/{issue_id}/pipeline"`` in ``pipelines_base/initiative.yaml``),
so it is factored here once rather than cloned in both gate modules
(design AG2 / DR2 mitigation, S14559.1 T3).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_INITIATIVE_RE = re.compile(r"initiative/(RAISE-\d+)/")


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
    except Exception:  # noqa: BLE001
        return ""


def resolve_initiative_key(working_dir: Path) -> str | None:
    r"""Resolve the running Initiative's issue key from the git branch.

    Returns ``None`` when the branch does not match
    ``initiative/(RAISE-\d+)/`` — callers treat this as fail-open (not
    applicable), matching the ``close_sync_gate`` precedent.
    """
    branch = _git_branch(working_dir)
    match = _INITIATIVE_RE.search(branch)
    return match.group(1) if match else None
