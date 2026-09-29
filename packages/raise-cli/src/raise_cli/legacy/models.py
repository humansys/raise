"""Pydantic boundary models for legacy residue detection.

``Residue`` and ``ScanReport`` are serialized by ``rai clean --json`` (S2)
and the session advisory (S4).  Ownership is derived from kind via a fixed
table -- call sites never pass it directly.

Architecture: Epic RAISE-16227 design §S1, I1.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal, get_args

from pydantic import BaseModel, model_validator

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

ResidueKind = Literal[
    # Owned (4) -- rai created these, rai can act on them
    "orphan-project-db",
    "orphan-global-partition",
    "stale-mcp-command",
    "stale-runtime-config",
    # Advisory project (13) -- rai detects, NEVER touches
    "venv-raise-cli",
    "venv-prerename-pkg",
    "venv-console-script",
    "venv-renamed",
    "path-shadowing",
    "requirements-dep",
    "pyproject-dep",
    "uvlock-entry",
    "user-mcp-dangling",
    "dangling-rai-symlink",
    "stale-cartridge-gen",
    "superseded-instance-files",
    "repo-cartridge-self-ingest",
    # Global advisory (3) -- outside the project
    "pipx-raise-cli",
    "user-site-raise-cli",
    "global-console-script",
    # Claude Code settings (1) -- env.PATH venv entries
    "claude-settings-path",
    # Owned -- developer.yaml orphan entries (S16227.8)
    "orphan-project-entry",
    "orphan-session-entry",
]

Ownership = Literal["owned", "advisory"]

OWNERSHIP_BY_KIND: dict[ResidueKind, Ownership] = {
    # Owned
    "orphan-project-db": "owned",
    "orphan-global-partition": "owned",
    "stale-mcp-command": "owned",
    "stale-runtime-config": "owned",
    # Advisory -- project
    "venv-raise-cli": "advisory",
    "venv-prerename-pkg": "advisory",
    "venv-console-script": "advisory",
    "venv-renamed": "advisory",
    "path-shadowing": "advisory",
    "requirements-dep": "advisory",
    "pyproject-dep": "advisory",
    "uvlock-entry": "advisory",
    "user-mcp-dangling": "advisory",
    "dangling-rai-symlink": "advisory",
    "stale-cartridge-gen": "advisory",
    "superseded-instance-files": "advisory",
    "repo-cartridge-self-ingest": "advisory",
    # Advisory -- global
    "pipx-raise-cli": "advisory",
    "user-site-raise-cli": "advisory",
    "global-console-script": "advisory",
    # Claude Code settings
    "claude-settings-path": "advisory",
    # Owned -- developer.yaml orphan entries (S16227.8)
    "orphan-project-entry": "owned",
    "orphan-session-entry": "owned",
}

# Family grouping for doctor check -- one CheckResult per family.
FAMILY_BY_KIND: dict[ResidueKind, str] = {
    "orphan-project-db": "dbs",
    "orphan-global-partition": "dbs",
    "stale-mcp-command": "configs",
    "stale-runtime-config": "configs",
    "venv-raise-cli": "venvs",
    "venv-prerename-pkg": "venvs",
    "venv-console-script": "venvs",
    "venv-renamed": "venvs",
    "path-shadowing": "path",
    "requirements-dep": "deps",
    "pyproject-dep": "deps",
    "uvlock-entry": "deps",
    "user-mcp-dangling": "configs",
    "dangling-rai-symlink": "global",
    "stale-cartridge-gen": "cartridges",
    "superseded-instance-files": "cartridges",
    "repo-cartridge-self-ingest": "cartridges",
    "pipx-raise-cli": "global",
    "user-site-raise-cli": "global",
    "global-console-script": "global",
    "claude-settings-path": "path",
    "orphan-project-entry": "developer-yaml",
    "orphan-session-entry": "developer-yaml",
}

# Sanity: every literal member is covered.
# Checked at module load time -- a missing entry is a programming error.
_all_kinds = set(get_args(ResidueKind))
if set(OWNERSHIP_BY_KIND.keys()) != _all_kinds:  # pragma: no cover
    _msg = f"OWNERSHIP_BY_KIND mismatch: {set(OWNERSHIP_BY_KIND.keys()) ^ _all_kinds}"
    raise RuntimeError(_msg)
if set(FAMILY_BY_KIND.keys()) != _all_kinds:  # pragma: no cover
    _msg = f"FAMILY_BY_KIND mismatch: {set(FAMILY_BY_KIND.keys()) ^ _all_kinds}"
    raise RuntimeError(_msg)


# ---------------------------------------------------------------------------
# Residue
# ---------------------------------------------------------------------------


class Residue(BaseModel):
    """A single detected legacy residue.

    Ownership is derived from ``kind`` via ``OWNERSHIP_BY_KIND``.
    Use ``Residue.create()`` to avoid passing ownership explicitly.
    """

    kind: ResidueKind
    path: Path
    ownership: Ownership
    evidence: dict[str, str] = {}
    action_hint: str = ""

    @model_validator(mode="after")
    def _check_ownership(self) -> Residue:
        expected = OWNERSHIP_BY_KIND[self.kind]
        if self.ownership != expected:
            msg = (
                f"Residue kind {self.kind!r} requires ownership "
                f"{expected!r}, got {self.ownership!r}"
            )
            raise ValueError(msg)
        return self

    @classmethod
    def create(
        cls,
        kind: ResidueKind,
        path: Path,
        *,
        evidence: dict[str, str] | None = None,
        action_hint: str = "",
    ) -> Residue:
        """Create a Residue with ownership derived from kind.

        Raises ``ValidationError`` if kind is not a valid ``ResidueKind``.
        """
        # Pydantic validates kind via the Literal type; but OWNERSHIP_BY_KIND
        # lookup would KeyError before that if called with a raw bad string.
        # Let Pydantic do the validation by passing ownership as a placeholder
        # that the model_validator will check.
        ownership = OWNERSHIP_BY_KIND.get(kind, "advisory")  # type: ignore[arg-type]
        return cls(
            kind=kind,
            path=path,
            ownership=ownership,
            evidence=evidence or {},
            action_hint=action_hint,
        )


# ---------------------------------------------------------------------------
# ScanReport
# ---------------------------------------------------------------------------


class ScanReport(BaseModel):
    """Aggregated result of a legacy scan pass."""

    project_root: Path
    residues: list[Residue] = []
    scanned_at: datetime
    scan_duration_ms: float

    @property
    def owned(self) -> list[Residue]:
        """Residues where rai can act."""
        return [r for r in self.residues if r.ownership == "owned"]

    @property
    def advisory(self) -> list[Residue]:
        """Residues that require manual action."""
        return [r for r in self.residues if r.ownership == "advisory"]

    def by_family(self) -> dict[str, list[Residue]]:
        """Group residues by family for doctor check output."""
        groups: dict[str, list[Residue]] = {}
        for r in self.residues:
            family = FAMILY_BY_KIND[r.kind]
            groups.setdefault(family, []).append(r)
        return groups
