"""SchemaRevisionsSyncGate — bijection check between SCHEMA_REVISIONS and migration files.

RAISE-20070: SCHEMA_REVISIONS in schema_revisions.py is maintained by hand.
When ``alembic revision`` generates a new file under
alembic_baseline/versions/{hash}_{name}.py, nothing previously enforced that
the same hash was added to SCHEMA_REVISIONS. A missing entry causes
_latest_schema_info() in build-version-manifest.py to silently publish a stale
schema_version/schema_revision in version.json.

This gate closes that loop: it asserts bijective consistency between the hash
prefixes of every migration filename and the values stored in SCHEMA_REVISIONS.

Filename parsing convention (Q2):
  alembic generates ``{12-hex-char-hash}_{slug}.py`` filenames (e.g.
  ``2fb8043dacd8_v82_baseline.py``). We extract the leading hex token (up to
  the first underscore) rather than importing each module and reading its
  ``revision`` attribute — importing migration files would execute module-level
  code and complicate the gate with alembic env setup. The convention is stable
  across alembic ≥1.7; a future rename would be caught by CI on the next run.

Gate IDs:
  gate-schema-revisions-sync        before:bug:close
  gate-schema-revisions-sync-story  before:story:close  (RAISE-20070 Q1)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.storage.schema_revisions import SCHEMA_REVISIONS

# Path from project root to the alembic versions directory.
_VERSIONS_RELPATH: Path = Path(
    "packages/raise-cli/src/raise_cli/storage/alembic_baseline/versions"
)

# Minimum length for a plausible alembic hex hash prefix.
_MIN_HASH_LEN: int = 10

# Pattern: leading hex characters before the first underscore.
_HASH_RE: re.Pattern[str] = re.compile(r"^([0-9a-f]+)_")


def _extract_file_hashes(versions_dir: Path) -> set[str]:
    """Return the set of hex hash prefixes found in migration filenames.

    Skips ``__init__.py`` and any file whose stem does not start with a
    well-formed hex hash (guards against hand-created helpers in the dir).
    """
    hashes: set[str] = set()
    for f in versions_dir.iterdir():
        if f.suffix != ".py" or f.name.startswith("__"):
            continue
        m = _HASH_RE.match(f.stem)
        if m and len(m.group(1)) >= _MIN_HASH_LEN:
            hashes.add(m.group(1))
    return hashes


def _evaluate_sync(context: GateContext, gate_id: str) -> GateResult:
    """Shared bijection logic for both workflow-point variants."""
    versions_dir = context.working_dir / _VERSIONS_RELPATH

    if not versions_dir.is_dir():
        return GateResult(
            passed=True,
            skipped=True,
            gate_id=gate_id,
            message=f"skipped: versions dir not found at {versions_dir}",
        )

    file_hashes = _extract_file_hashes(versions_dir)
    dict_hashes: set[str] = set(SCHEMA_REVISIONS.values())

    in_files_not_dict = file_hashes - dict_hashes
    in_dict_not_files = dict_hashes - file_hashes

    if not in_files_not_dict and not in_dict_not_files:
        n = len(file_hashes)
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"schema revisions in sync: {n} revision(s)",
        )

    details: list[str] = []
    if in_files_not_dict:
        orphans = ", ".join(sorted(in_files_not_dict))
        details.append(f"Migration files with no entry in SCHEMA_REVISIONS: {orphans}")
        details.append(
            "Fix: add the missing {version: 'hash'} entry to"
            " packages/raise-cli/src/raise_cli/storage/schema_revisions.py"
        )
    if in_dict_not_files:
        orphans = ", ".join(sorted(in_dict_not_files))
        details.append(
            f"SCHEMA_REVISIONS values with no corresponding migration file: {orphans}"
        )
        details.append(
            "Fix: check whether the migration file was deleted or the hash is wrong"
        )

    return GateResult(
        passed=False,
        gate_id=gate_id,
        message=(
            f"SCHEMA_REVISIONS out of sync — "
            f"{len(in_files_not_dict)} hash(es) in files but not in dict, "
            f"{len(in_dict_not_files)} hash(es) in dict but not in files"
        ),
        details=tuple(details),
    )


class SchemaRevisionsSyncGate:
    """Verify SCHEMA_REVISIONS is in bijection with alembic_baseline/versions/*.py.

    Registered via ``rai.gates`` entry point.
    Workflow point: before:bug:close
    """

    gate_id: ClassVar[str] = "gate-schema-revisions-sync"
    description: ClassVar[str] = (
        "SCHEMA_REVISIONS dict stays in bijection with alembic_baseline/versions/*.py"
    )
    workflow_point: ClassVar[str] = "before:bug:close"

    def evaluate(self, context: GateContext) -> GateResult:  # noqa: D102
        return _evaluate_sync(context, self.gate_id)


class SchemaRevisionsSyncStoryGate:
    """Same bijection check at story-close time (RAISE-20070 Q1).

    Stories may also introduce Alembic migrations, so the check must run at
    before:story:close as well.

    Workflow point: before:story:close
    """

    gate_id: ClassVar[str] = "gate-schema-revisions-sync-story"
    description: ClassVar[str] = (
        "SCHEMA_REVISIONS dict stays in bijection with alembic_baseline/versions/*.py"
        " (story close)"
    )
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:  # noqa: D102
        return _evaluate_sync(context, self.gate_id)
