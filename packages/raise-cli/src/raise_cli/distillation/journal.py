"""Session journal builder for the post-session distillation agent.

Builds structured Markdown from classified TurnRecords and writes
it to ~/.rai/journals/YYYY-MM-DD-{session_id}.md.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from raise_cli.distillation.classifier import TurnClass
from raise_cli.distillation.parser import TurnRecord

_DELIMITERS = re.compile(r"\s*[—–]\s*|\s*,\s+|\s+-\s+")

_CLASS_DEFAULTS: dict[TurnClass, int] = {
    TurnClass.CORRECTION: 4,
    TurnClass.INSIGHT: 5,
    TurnClass.DECISION: 3,
    TurnClass.BLOCKER: 5,
    TurnClass.TOOL_USE: 1,
    TurnClass.TOOL_REJECTION: 1,
    TurnClass.NEUTRAL: 1,
}

_ACTIONABLE_CLASSES = frozenset(
    {
        TurnClass.CORRECTION,
        TurnClass.INSIGHT,
        TurnClass.DECISION,
        TurnClass.BLOCKER,
    }
)

_ACTION_TEMPLATES: dict[TurnClass, str] = {
    TurnClass.CORRECTION: "avoid: {action}",
    TurnClass.INSIGHT: "{action}",
    TurnClass.DECISION: "approved — proceed",
    TurnClass.BLOCKER: "STOP — {action}",
}


def _snippet(text: str, max_chars: int = 200) -> str:
    text = text.strip().replace("\n", " ")
    return text[:max_chars] + "…" if len(text) > max_chars else text


def default_utility(cls: TurnClass) -> int:
    """Return the default utility score for a turn class."""
    return _CLASS_DEFAULTS.get(cls, 1)


def _split_trigger_action(text: str) -> tuple[str, str]:
    """Split text into trigger context and action content."""
    clean = text.strip().replace("\n", " ")
    parts = _DELIMITERS.split(clean, maxsplit=1)
    if len(parts) == 2 and len(parts[0]) > 3:
        return _snippet(parts[0], 80), _snippet(parts[1], 120)
    return _snippet(clean, 80), _snippet(clean, 120)


def render_trigger_action(
    record: TurnRecord,
    cls: TurnClass,
    confidence: int | None = None,
) -> str:
    """Render a classified turn as a trigger-action heuristic.

    Returns empty string for non-actionable classes (neutral, tool_use, tool_rejection).
    """
    if cls not in _ACTIONABLE_CLASSES:
        return ""

    utility = confidence if confidence is not None else default_utility(cls)
    trigger, action_raw = _split_trigger_action(record.content_text)

    template = _ACTION_TEMPLATES[cls]
    action = template.format(action=action_raw) if "{action}" in template else template

    return f"- when [{trigger}], then [{action}] (utility: {utility}/5)"


def _build_pipeline_runs_section(records: list[TurnRecord]) -> list[str]:
    """Build the Pipeline Runs section lines from records with [RAI:] headers."""
    pipeline_records = [r for r in records if r.rai_header is not None]
    lines: list[str] = ["## Pipeline Runs", ""]
    if not pipeline_records:
        lines.append("_No structured [RAI:] headers detected._")
        return lines
    runs: dict[str, list[TurnRecord]] = {}
    for r in pipeline_records:
        if r.rai_header:
            run_id = r.rai_header.get("run_id", "unknown")
            runs.setdefault(run_id, []).append(r)
    for run_id, run_records in runs.items():
        first = run_records[0].rai_header or {}
        skill = first.get("skill", "?")
        parent = first.get("parent_session", "?")
        lines.append(
            f"- **run_id:** `{run_id}` | skill: `{skill}` | parent: `{parent}`"
        )
        for r in run_records:
            h = r.rai_header or {}
            lines.append(f"  - turn {r.index}: phase=`{h.get('phase', '?')}`")
    return lines


def build_journal_md(
    session_id: str,
    date: str,
    records: list[TurnRecord],
    classes: list[TurnClass],
    *,
    confidences: list[int] | None = None,
) -> str:
    """Build journal Markdown from classified records.

    Groups turns by class into sections. When RAISE_DISTILL_TRIGGER_ACTION
    is enabled (default), renders actionable classes as trigger-action
    heuristics. Adds a pipeline_runs section when [RAI:] headers are present.
    """
    use_trigger_action = os.environ.get("RAISE_DISTILL_TRIGGER_ACTION", "1") != "0"

    conf_map: dict[int, int] = (
        dict(enumerate(confidences)) if confidences is not None else {}
    )

    buckets: dict[TurnClass, list[tuple[TurnRecord, TurnClass, int | None]]] = {
        c: [] for c in TurnClass
    }
    for idx, (record, cls) in enumerate(zip(records, classes, strict=False)):
        buckets[cls].append((record, cls, conf_map.get(idx)))

    lines: list[str] = [
        f"# Session Journal: {date} — {session_id}",
        "",
        f"**Turns:** {len(records)} | **Date:** {date}",
        "",
    ]

    for cls, label in [
        (TurnClass.DECISION, "Decisions"),
        (TurnClass.CORRECTION, "Corrections"),
        (TurnClass.TOOL_REJECTION, "Tool Rejections"),
        (TurnClass.INSIGHT, "Insights"),
        (TurnClass.BLOCKER, "Blockers"),
    ]:
        items = buckets[cls]
        lines.append(f"## {label}")
        lines.append("")
        if not items:
            lines.append("_None detected._")
        else:
            for record, record_cls, conf in items:
                if use_trigger_action:
                    ta = render_trigger_action(record, record_cls, confidence=conf)
                    if ta:
                        lines.append(ta)
                    else:
                        lines.append(
                            f"- [turn {record.index}] {_snippet(record.content_text)}"
                        )
                else:
                    lines.append(
                        f"- [turn {record.index}] {_snippet(record.content_text)}"
                    )
        lines.append("")

    lines.extend(_build_pipeline_runs_section(records))
    lines.append("")

    return "\n".join(lines)


def write_journal(content: str, session_id: str, date: str) -> Path:
    """Write journal to ~/.rai/journals/YYYY-MM-DD-{session_id}.md."""
    journals_dir = Path.home() / ".rai" / "journals"
    journals_dir.mkdir(parents=True, exist_ok=True)
    path = journals_dir / f"{date}-{session_id}.md"
    path.write_text(content, encoding="utf-8")
    return path
