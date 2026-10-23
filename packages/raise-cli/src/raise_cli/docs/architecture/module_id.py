"""Module id resolution for a curated architecture doc (RAISE-16033 C1).

``rai docs architecture status`` (``cli/commands/docs_architecture.py``)
and ``ArchitectureDocsFreshGate`` (``gates/docs_architecture.py``) both
need the graph's ``mod-*`` id for a doc under
``governance/architecture/modules/`` so they can look its bundle up in
the graph and compare fingerprints. Before RAISE-16033 every id was the
bare ``mod-<filename-stem>`` — deriving it from the doc's filename alone
was safe because ids were never package-qualified.

Discovery now mints ``mod-<package>--<module>`` for anything under
``packages/*`` (``raise_core.discovery.symbols.qualified_module_id``,
the RAISE-16033 C1 single source of truth), and the curated sidecar
loader (``raise_cli.context.loaders.architecture``) mints the same
qualified id from the sidecar's ``package:`` field. A bare stem-derived
id in these two doc-driven consumers would silently stop matching the
qualified graph node — the fingerprint gate would report "module not in
graph" (fail-open) instead of actually checking staleness, disabling the
check for every package-qualified module.

This module is the single place both consumers resolve a doc's id, so
all three id-minting sites (discovery, curated sidecar loader, doc
consumers) agree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from raise_core.discovery.symbols import qualified_module_id


def module_id_for_doc(doc_path: Path) -> str:
    """Resolve the graph ``mod-*`` id for a module doc.

    Reads the doc's YAML frontmatter for ``name``/``package`` and
    package-qualifies via ``qualified_module_id`` — the same rule
    discovery scans and the curated sidecar loader use. Falls back to
    the bare filename stem (and no package qualifier) when frontmatter
    is missing, malformed, or absent, so a doc without the frontmatter
    convention still resolves exactly as it always did.
    """
    name: str = doc_path.stem
    package: str | None = None

    try:
        text = doc_path.read_text(encoding="utf-8")
    except OSError:
        text = ""

    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            try:
                data: Any = yaml.safe_load(text[4:end])
            except yaml.YAMLError:
                data = None
            if isinstance(data, dict):
                raw_name = data.get("name")
                if isinstance(raw_name, str) and raw_name:
                    name = raw_name
                raw_package = data.get("package")
                if isinstance(raw_package, str) and raw_package:
                    package = raw_package

    return qualified_module_id(name, package)
