"""Learning record model and I/O for the LEARN protocol.

Produces and reads flat YAML learning records that capture structured
signals from skill executions: pattern votes, gaps, artifact pointers.

Schema matches aspects/introspection.md § Learning Record Schema.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PatternVote(BaseModel):
    """Vote on a primed pattern's usefulness during skill execution.

    Distinct from memory reinforcement (cumulative). This is per-execution
    evaluation: +1 (used), 0 (seen, not relevant), -1 (misleading).
    """

    vote: Literal[-1, 0, 1]
    why: str = Field(
        ..., min_length=1, description="Reason for the vote — the signal, not the number"
    )


class LearningRecord(BaseModel):
    """Flat learning record produced by LEARN protocol.

    Schema matches aspects/introspection.md § Learning Record Schema.
    ~10 fields, pointers not traces.
    """

    skill: str
    work_id: str
    version: str
    timestamp: datetime
    primed_patterns: list[str] = Field(default_factory=list)
    tier1_queries: int = Field(default=0, ge=0)
    tier1_results: int = Field(default=0, ge=0)
    jit_queries: int = Field(default=0, ge=0)
    pattern_votes: dict[str, PatternVote] = Field(default_factory=dict)
    gaps: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    commit: str | None = None
    branch: str | None = None
    downstream: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Downstream enrichment fields. Intentionally open (dict[str, Any]) — "
            "schema will be tightened after dogfood (S1133.6). AR-R2."
        ),
    )


def write_record(record: LearningRecord, base_dir: Path) -> Path:
    """Write learning record to .raise/rai/learnings/{skill}/{work_id}/record.yaml.

    Creates directories as needed. Overwrites existing record (rework overwrites
    per schema rules).

    Args:
        record: The learning record to write.
        base_dir: Project root directory.

    Returns:
        Path to the written YAML file.
    """
    record_dir = base_dir / ".raise" / "rai" / "learnings" / record.skill / record.work_id
    record_dir.mkdir(parents=True, exist_ok=True)

    record_path = record_dir / "record.yaml"
    data = record.model_dump(mode="json")
    record_path.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return record_path


def read_record(skill: str, work_id: str, base_dir: Path) -> LearningRecord | None:
    """Read learning record. Returns None if not found (silent node or not yet written).

    Never raises on missing/corrupted file — returns None.

    Args:
        skill: Skill name (e.g., "rai-story-design").
        work_id: Work item ID (e.g., "S1133.1").
        base_dir: Project root directory.

    Returns:
        LearningRecord if found and valid, None otherwise.
    """
    record_path = (
        base_dir / ".raise" / "rai" / "learnings" / skill / work_id / "record.yaml"
    )
    if not record_path.exists():
        return None

    try:
        data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return LearningRecord.model_validate(data)
    except Exception:
        logger.warning("Failed to parse learning record at %s", record_path, exc_info=True)
        return None
