"""Shared file-level classification for cartridge ``instances/`` directories.

``instances/`` is a mixed directory: per-spec node-list files (each a JSON
*list* of node dicts) plus sidecar files that hold cartridge metadata and are
never node lists:

- ``embedding_index.json`` — ``{node_id: row_index}``, written by
  ``write_embeddings()`` (embedding.py) after ``rai graph build``. Present in
  6 cartridges in this repo today.
- ``synonyms.json`` — hand-authored ``{"groups": [[...], ...]}`` vocabulary
  map, read by ``load_synonyms()`` (synonyms.py). Present in 4 cartridges.
- ``manifest.json`` / ``fingerprints.json`` / ``spec.json`` — the atomic
  embedding-generation scheme (``write_embeddings_atomic()``). Zero
  occurrences in this repo today, but real production sidecars, not
  hypothetical.

Iterating any of these at the item level yields plain strings (dict keys)
instead of node dicts, which fails ``GraphNode`` validation with a confusing
``model_type`` error (RAISE-15998).

Any call site that wants node files must exclude these sidecars at the FILE
level, before the file is ever read — never at the item level. Call sites
that also *write back* to every file they discovered (e.g.
``relate.ingest_relationship_work``) would otherwise truncate the sidecars to
``[]`` on write, destroying the embedding index / synonym config. This module
is the single place that owns the "which files are sidecars" decision so it
never has to be answered ad hoc again (epic RAISE-15985 S2).
"""

from __future__ import annotations

from pathlib import Path

INSTANCE_SIDECAR_FILES: frozenset[str] = frozenset(
    {
        "embedding_index.json",
        "synonyms.json",
        "manifest.json",
        "fingerprints.json",
        "spec.json",
    }
)


def iter_instance_files(instances_dir: Path) -> list[Path]:
    """Return the ``instances_dir/*.json`` files that hold node lists.

    Excludes known non-node sidecars (see module docstring). Sorted for a
    deterministic iteration order, matching every prior glob-based call site.
    Non-recursive, matching ``Path.glob("*.json")`` — sidecars written inside
    a nested generation directory are already outside this glob's reach.
    """
    return sorted(
        p for p in instances_dir.glob("*.json") if p.name not in INSTANCE_SIDECAR_FILES
    )


__all__ = ["INSTANCE_SIDECAR_FILES", "iter_instance_files"]
