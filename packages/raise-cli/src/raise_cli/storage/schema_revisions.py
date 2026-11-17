"""Alembic revision IDs for each schema version — RAISE-19634.

Two sources of authority for the raise-cli DB schema:
  - PRAGMA user_version  : versions 0–82 (hand-rolled _apply_vXX engine)
  - alembic_version table: versions 83+  (Alembic, with downgrade())

This module provides the mapping from schema_version (int) to Alembic revision
ID (str) so that build scripts and ``core/manifest.py`` can reference the same
constant without importing the storage layer.

No imports from raise_cli — this module is read by scripts/build-version-manifest.py
via importlib without the package being installed.
"""

from __future__ import annotations

# Maps integer schema_version to the Alembic hex revision ID published in
# version.json as ``schema_revision``.
# The baseline revision "2fb8043dacd8" corresponds to the v82 snapshot: it only
# creates alembic_version and stamps the DB — it does NOT re-run _apply_v0.._apply_v82.
SCHEMA_REVISIONS: dict[int, str] = {
    82: "2fb8043dacd8",
}
