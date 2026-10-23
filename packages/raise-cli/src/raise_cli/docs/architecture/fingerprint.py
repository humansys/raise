"""Canonical fingerprint over a SynthesisBundle (D-S5, AC5).

The allowlist IS ``SynthesisBundle``'s field set (see models.py docstring):
this function does not need its own denylist because volatile fields
(``created``, ``updated_at``, ``rank``, ``score``, ``execution_time_ms``,
absolute ``source_file`` paths) are never present on the bundle to begin
with. Canonicalization here only has to worry about a second source of
instability: unordered lists / dict key order.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from raise_cli.docs.architecture.models import SynthesisBundle


def _canonical_payload(bundle: SynthesisBundle) -> dict[str, Any]:
    """Build the sorted, order-independent dict fingerprinted below.

    Excludes ``fingerprint`` itself (it is an output, not an input) so
    that a previously-stamped value never participates in its own hash.
    """
    symbols = sorted((s.name, s.kind, s.file) for s in bundle.symbols)
    return {
        "module_id": bundle.module_id,
        "name": bundle.name,
        "purpose": bundle.purpose,
        "depends_on": sorted(bundle.depends_on),
        "depended_by": sorted(bundle.depended_by),
        "public_api": sorted(bundle.public_api),
        "entry_points": sorted(bundle.entry_points),
        "code_imports": sorted(bundle.code_imports),
        "code_exports": sorted(bundle.code_exports),
        "code_components": bundle.code_components,
        "symbols": symbols,
    }


def fingerprint(bundle: SynthesisBundle) -> str:
    """Compute the canonical ``sha256:...`` fingerprint of a bundle's input.

    Two bundles that differ only in field order, list order, or a stale
    ``bundle.fingerprint`` value from a previous run hash identically.
    A real change to any allowlisted field changes the result.
    """
    payload = _canonical_payload(bundle)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
