"""ADR-146 region parser and byte-slice writer.

Regions are located by **byte offset**, never by markdown-AST node —
that is what makes preservation (AC2) true by construction: the writer
splices a byte range and never re-serializes the surrounding document, so
prose outside ``[begin_marker_start, end_marker_end]`` is untouched.

Marker shape (ADR-146 A146.1, with ``src``/``hash`` added per S15884.2
D-S3)::

    <!-- rai:auto:begin id="c4-component" generator="layer2" src="sha256:..." hash="sha256:..." -->
    ...generated content...
    <!-- rai:auto:end id="c4-component" -->

Orphan detection (AC3) is a single linear scan with a one-element stack:
``begin`` without ``end``, ``end`` without ``begin``, duplicate ``id``,
and nested markers all raise ``OrphanMarkerError`` before any write is
attempted — noisy failure, never a partial write (ADR-146 A146.2).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from raise_cli.docs.architecture.models import Region, RegionWriteResult

_MARKER_RE = re.compile(r"<!--\s*rai:auto:(begin|end)\s+(.*?)-->\n?", re.DOTALL)
_ATTR_RE = re.compile(r'(\w+)="([^"]*)"')

DEFAULT_GENERATOR = "layer2"


class OrphanMarkerError(ValueError):
    """A ``rai:auto`` marker is malformed — begin/end pair broken.

    Raised for: begin without end, end without begin, duplicate id, or
    nested markers. Never raised alongside a partial write — callers must
    treat this as "nothing was written."
    """


class PayloadContainsMarkerError(ValueError):
    """A synthesized payload itself contains ``rai:auto:begin``/``:end``.

    Since the LLM-synthesized narrative could plausibly (having just read
    SKILL.md/ADR-146 text containing marker syntax) echo one of these
    substrings into its own output, writing it verbatim would embed a
    stray marker inside the region body — every subsequent
    ``parse_regions`` call then raises ``OrphanMarkerError`` and the doc
    becomes unwritable/unparseable via normal tooling until hand-repaired
    (R2). Raised before any write is attempted.
    """


_FORBIDDEN_PAYLOAD_SUBSTRINGS = ("rai:auto:begin", "rai:auto:end")


def _reject_embedded_markers(payload: str) -> None:
    for token in _FORBIDDEN_PAYLOAD_SUBSTRINGS:
        if token in payload:
            raise PayloadContainsMarkerError(
                f"payload contains a literal '{token}' substring — writing "
                "it verbatim would embed a stray rai:auto marker inside "
                "the region body, permanently corrupting the doc for every "
                "subsequent parse. No write performed; strip the literal "
                "marker text from the synthesized content and retry."
            )


def parse_regions(text: str) -> list[Region]:
    """Parse all ``rai:auto`` regions out of ``text``.

    Returns an empty list when no markers are present (the common case
    for the 22 pre-existing module docs — insertion, not overwrite).

    Raises:
        OrphanMarkerError: malformed marker structure (see class docstring).
    """
    stack: list[dict[str, object]] = []
    regions: list[Region] = []
    seen_ids: set[str] = set()

    for match in _MARKER_RE.finditer(text):
        kind = match.group(1)
        attrs = dict(_ATTR_RE.findall(match.group(2)))
        marker_id = attrs.get("id")
        if not marker_id:
            raise OrphanMarkerError(
                f"rai:auto:{kind} marker missing id= attribute at offset {match.start()}"
            )

        if kind == "begin":
            if stack:
                outer_id = stack[-1]["id"]
                raise OrphanMarkerError(
                    f'nested marker: begin id="{marker_id}" found inside '
                    f'still-open region id="{outer_id}"'
                )
            if marker_id in seen_ids:
                raise OrphanMarkerError(f'duplicate region id="{marker_id}"')
            seen_ids.add(marker_id)
            stack.append({"id": marker_id, "attrs": attrs, "match": match})
        else:  # end
            if not stack:
                raise OrphanMarkerError(
                    f'rai:auto:end id="{marker_id}" has no matching begin'
                )
            top = stack.pop()
            if top["id"] != marker_id:
                raise OrphanMarkerError(
                    f'mismatched marker: end id="{marker_id}" does not close '
                    f'begin id="{top["id"]}"'
                )
            begin_match = top["match"]
            begin_attrs = top["attrs"]
            assert isinstance(begin_match, re.Match)  # noqa: S101 — internal invariant
            assert isinstance(begin_attrs, dict)  # noqa: S101 — internal invariant
            regions.append(
                Region(
                    id=marker_id,
                    generator=begin_attrs.get("generator", ""),
                    src=begin_attrs.get("src", ""),
                    hash=begin_attrs.get("hash", ""),
                    begin_start=begin_match.start(),
                    begin_end=begin_match.end(),
                    end_start=match.start(),
                    end_end=match.end(),
                    body=text[begin_match.end() : match.start()],
                )
            )

    if stack:
        unmatched_id = stack[-1]["id"]
        raise OrphanMarkerError(
            f'rai:auto:begin id="{unmatched_id}" has no matching end'
        )

    return regions


def _normalize_payload(payload: str) -> str:
    """LF endings, strip per-line trailing whitespace, one trailing newline."""
    text = payload.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    normalized = "\n".join(lines)
    return normalized.rstrip("\n") + "\n"


def _content_hash(normalized_payload: str) -> str:
    digest = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _build_marker_block(
    region_id: str, generator: str, src: str, content_hash: str, normalized_payload: str
) -> str:
    begin = (
        f'<!-- rai:auto:begin id="{region_id}" generator="{generator}" '
        f'src="{src}" hash="{content_hash}" -->\n'
    )
    end = f'<!-- rai:auto:end id="{region_id}" -->\n'
    return begin + normalized_payload + end


def region_hash_matches(region: Region) -> bool:
    """True when a region's current bytes still match its stored ``hash``.

    False means a human edited inside a machine-owned region (D-S3 table:
    hash mismatch -> warn loudly before the next run clobbers it). Body is
    renormalized before comparing so trivial whitespace reformatting is not
    mistaken for tampering — the same tolerance ``write_region`` itself
    applies to incoming payloads.
    """
    return region.hash == _content_hash(_normalize_payload(region.body))


def write_region(
    path: Path,
    region_id: str,
    payload: str,
    src: str,
    *,
    generator: str = DEFAULT_GENERATOR,
    dry_run: bool = False,
) -> RegionWriteResult:
    """Write ``payload`` into the ``region_id`` region of ``path``.

    Implements the D-S3 write algorithm:

    1. Parse existing regions (raises ``OrphanMarkerError``, writes nothing,
       on malformed markers — AC3).
    2. Normalize the payload.
    3. If the region exists and both stored ``hash`` and ``src`` already
       match -> return ``changed=False`` **without opening the file for
       write** (AC1: mtime untouched, zero-cost no-op).
    4. If the region exists and differs -> replace the byte slice between
       markers in place.
    5. If the region is absent -> insert a new block at the canonical
       anchor (end of file).

    Every byte outside ``[begin_start, end_end]`` of the *matched* region
    is carried through unchanged by construction (AC2) — this function
    only ever slices the original text, never re-serializes it.

    Args:
        path: Target markdown doc. Not required to exist yet (insert case).
        region_id: The ``id=`` attribute identifying which region to write.
        payload: Synthesized content to place inside the region (normalized
            before hashing/writing).
        src: Caller-supplied input fingerprint, stored on the begin marker
            so a later reader can compare it to a freshly computed one.
        generator: Recorded on the begin marker's ``generator=`` attribute.
        dry_run: When True, run the exact same hash/fingerprint comparison
            used to decide whether a write would occur, and return the
            would-be action/hash/preview — but never call
            ``path.write_text`` (C3). This is the staging half of a
            stage -> approve -> commit-to-disk flow: callers run this
            first to produce a human-reviewable diff, then call again
            with ``dry_run=False`` only after that diff is approved.

    Raises:
        PayloadContainsMarkerError: ``payload`` itself contains a literal
            ``rai:auto:begin``/``:end`` substring (R2) — checked before
            anything else, so nothing is written.
    """
    _reject_embedded_markers(payload)

    existing_text = path.read_text(encoding="utf-8") if path.exists() else ""

    regions = parse_regions(
        existing_text
    )  # OrphanMarkerError propagates, nothing written

    normalized = _normalize_payload(payload)
    computed_hash = _content_hash(normalized)

    match = next((r for r in regions if r.id == region_id), None)

    if match is not None and match.hash == computed_hash and match.src == src:
        return RegionWriteResult(
            changed=False,
            action="unchanged",
            region_id=region_id,
            path=str(path),
            hash=computed_hash,
            message=f"unchanged: {path}#{region_id} (no write)",
        )

    block = _build_marker_block(region_id, generator, src, computed_hash, normalized)
    action = "replaced" if match is not None else "inserted"

    if dry_run:
        verb = "would replace" if action == "replaced" else "would insert"
        return RegionWriteResult(
            changed=True,
            action=action,
            region_id=region_id,
            path=str(path),
            hash=computed_hash,
            message=f"[dry-run] {verb}: {path}#{region_id} (hash {computed_hash})",
            preview=block,
        )

    if match is not None:
        new_text = (
            existing_text[: match.begin_start] + block + existing_text[match.end_end :]
        )
    else:
        prefix = existing_text
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        if prefix:
            prefix += "\n"
        new_text = prefix + block

    path.write_text(new_text, encoding="utf-8")

    verb = "inserted" if action == "inserted" else "replaced"
    return RegionWriteResult(
        changed=True,
        action=action,
        region_id=region_id,
        path=str(path),
        hash=computed_hash,
        message=f"{verb}: {path}#{region_id} (hash {computed_hash})",
    )
