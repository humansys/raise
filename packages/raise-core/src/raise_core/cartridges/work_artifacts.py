"""Work artifacts cartridge generator — index decisions, retros, designs from work/epics/."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

_ADR_RE = re.compile(r"\bADR-\d{3}\b")


def detect_supersession(content: str) -> str | None:
    """Extract the highest-numbered ADR-NNN reference from content, or None."""
    matches = _ADR_RE.findall(content)
    if not matches:
        return None
    return max(set(matches), key=lambda m: int(m.split("-")[1]))


_FILE_TYPE_PATTERNS: dict[str, str] = {
    "retrospective": "retrospective",
    "design": "design_doc",
    "story": "decision",
    "scope": "design_doc",
    "plan": "design_doc",
    "journal": "journal_entry",
}

_STORY_ID_RE = re.compile(r"^s(\d+\.\d+)-")
_EPIC_ID_RE = re.compile(r"^e(.+?)(?:-|$)")


def classify_work_file(filename: str) -> str | None:
    """Classify a markdown file by its filename pattern.

    Returns the node type string, or None if unrecognized.
    """
    stem = Path(filename).stem
    for pattern, node_type in _FILE_TYPE_PATTERNS.items():
        if pattern in stem.split("-"):
            return node_type
        if stem == pattern:
            return node_type
    return None


def _extract_epic_id(epic_dirname: str) -> str:
    """Extract epic ID from directory name like 'e1305-mcp-skill-runtime'."""
    m = _EPIC_ID_RE.match(epic_dirname)
    return m.group(1) if m else epic_dirname


def _extract_story_id(filename: str) -> str | None:
    """Extract story ID from filename like 's1305.2-retrospective.md'."""
    m = _STORY_ID_RE.match(filename)
    return f"s{m.group(1)}" if m else None


def _make_node_id_for_file(
    epic_id: str,
    story_id: str | None,
    filename: str,
) -> str:
    """Build deterministic node ID, disambiguating epic-level files by stem."""
    if story_id:
        artifact_key = (
            Path(filename).stem.split("-", 1)[-1]
            if "-" in Path(filename).stem
            else Path(filename).stem
        )
        return f"wa-e{epic_id}-{story_id}-{artifact_key}"
    return f"wa-e{epic_id}-{Path(filename).stem}"


def generate_work_artifacts_cartridge(
    work_dir: Path,
    output_dir: Path,
    *,
    cartridge_name: str = "work-artifacts",
) -> Path:
    """Generate a work-artifacts cartridge from work/epics/ directory tree."""
    cartridge_dir = output_dir / cartridge_name
    cartridge_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    nodes: list[dict[str, object]] = []

    for epic_path in sorted(work_dir.iterdir()):
        if not epic_path.is_dir():
            continue

        epic_id = _extract_epic_id(epic_path.name)

        for md_file in sorted(epic_path.glob("*.md")):
            node_type = classify_work_file(md_file.name)
            if node_type is None:
                continue
            content = md_file.read_text(encoding="utf-8")
            node_id = _make_node_id_for_file(epic_id, None, md_file.name)
            nodes.append(
                {
                    "id": node_id,
                    "type": node_type,
                    "content": content,
                    "source_file": str(md_file.relative_to(work_dir.parent)),
                    "created": now,
                    "metadata": {
                        "cartridge": cartridge_name,
                        "epic_id": epic_id,
                        "artifact_type": node_type,
                        "temporal": {
                            "valid_from": now,
                            "superseded_by": detect_supersession(content),
                        },
                    },
                }
            )

        stories_dir = epic_path / "stories"
        if not stories_dir.is_dir():
            continue

        for md_file in sorted(stories_dir.glob("*.md")):
            node_type = classify_work_file(md_file.name)
            if node_type is None:
                continue
            content = md_file.read_text(encoding="utf-8")
            story_id = _extract_story_id(md_file.name)
            node_id = _make_node_id_for_file(epic_id, story_id, md_file.name)
            nodes.append(
                {
                    "id": node_id,
                    "type": node_type,
                    "content": content,
                    "source_file": str(md_file.relative_to(work_dir.parent)),
                    "created": now,
                    "metadata": {
                        "cartridge": cartridge_name,
                        "epic_id": epic_id,
                        "story_id": story_id,
                        "artifact_type": node_type,
                        "temporal": {
                            "valid_from": now,
                            "superseded_by": detect_supersession(content),
                        },
                    },
                }
            )

    (instances_dir / "work-artifacts.json").write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    manifest = {
        "name": cartridge_name,
        "display_name": "Work Artifacts",
        "version": "1.0.0",
        "schema": {
            "module": "raise_core.graph.models",
            "class_name": "GraphNode",
        },
        "source": {
            "type": "derived",
            "authority": "local",
            "generator": "raise_core.cartridges.work_artifacts:generate_work_artifacts_cartridge",
            "refresh": "manual",
        },
    }
    (cartridge_dir / "CARTRIDGE.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False),
        encoding="utf-8",
    )

    return cartridge_dir
