"""Post-session distillation agent — orchestrator and CLI entry point.

Usage:
    python -m raise_cli.distillation.agent --project .
    python -m raise_cli.distillation.agent --session /path/to/session.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.memory.patterns_backend import get_patterns_backend

logger = logging.getLogger(__name__)


async def distill(
    jsonl_path: Path,
    *,
    runtime: str = "claude-code",
    project: str = "",
    use_llm: bool | None = None,
    backend: str | None = None,
    two_stage: bool | None = None,
) -> None:
    """Parse, classify, persist patterns, write journal, and persist run to SQLite.

    When RAISE_DISTILLATION_LLM=1 (or use_llm=True), uses the LLM batch classifier
    instead of the heuristic classifier. The backend can be selected explicitly via
    --backend or RAISE_DISTILLATION_BACKEND env var (default: deepseek).

    When two_stage=True (or RAISE_DISTILLATION_TWO_STAGE=1), runs a second CoT
    verification pass on Stage-1 INSIGHT candidates to reduce false positives (AC4).
    Stage 2 is only applied when LLM mode is enabled.
    """
    from raise_cli.distillation.classifier import TurnClass, classify_turn
    from raise_cli.distillation.journal import build_journal_md, write_journal
    from raise_cli.distillation.parser import parse_session_jsonl
    from raise_cli.distillation.storage import DistillationRun, persist_run
    from raise_cli.storage.connection import get_global_db

    records = parse_session_jsonl(jsonl_path)

    _use_llm = (
        use_llm
        if use_llm is not None
        else os.environ.get("RAISE_DISTILLATION_LLM") == "1"
    )
    _two_stage = (
        two_stage
        if two_stage is not None
        else os.environ.get("RAISE_DISTILLATION_TWO_STAGE") == "1"
    )
    confidences: list[int] | None = None
    if _use_llm:
        from raise_cli.distillation.llm_classifier import (
            apply_two_stage,
            classify_turns_llm_with_confidence,
        )

        pairs = classify_turns_llm_with_confidence(records, backend=backend)
        classes = [cls for cls, _ in pairs]
        confidences = [conf for _, conf in pairs]
        if _two_stage:
            resolved_backend = backend or os.environ.get(
                "RAISE_DISTILLATION_BACKEND", "deepseek"
            )
            logger.info("Two-stage verification enabled (backend=%s)", resolved_backend)
            classes = apply_two_stage(records, classes, backend=resolved_backend)
    else:
        classes = [classify_turn(r) for r in records]

    # Persist detected patterns (non-fatal — journal/DB write must succeed regardless)
    patterns_backend = get_patterns_backend()
    pattern_count = 0
    for record, cls in zip(records, classes, strict=False):
        if cls == TurnClass.INSIGHT:
            snippet = record.content_text[:300].strip()
            if not snippet:
                continue
            try:
                await patterns_backend.add(
                    content=snippet,
                    context_tags=["distillation", "auto"],
                    pattern_type="process",
                    from_story="distillation-agent",
                )
                pattern_count += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("Pattern persistence skipped: %s", exc)

    # Build and write journal
    session_id = jsonl_path.stem
    date = datetime.now(UTC).strftime("%Y-%m-%d")
    content = build_journal_md(
        session_id, date, records, classes, confidences=confidences
    )
    journal_path = write_journal(content, session_id, date)

    decisions = sum(1 for c in classes if c == TurnClass.DECISION)
    corrections = sum(1 for c in classes if c == TurnClass.CORRECTION)
    blockers = sum(1 for c in classes if c == TurnClass.BLOCKER)
    tool_use_count = sum(1 for c in classes if c == TurnClass.TOOL_USE)

    # Persist run to SQLite
    run = DistillationRun(
        session_id=session_id,
        date=date,
        project=project,
        runtime=runtime,
        turns_total=len(records),
        decisions_count=decisions,
        corrections_count=corrections,
        patterns_count=pattern_count,
        blockers_count=blockers,
        tool_use_count=tool_use_count,
        journal_path=str(journal_path),
        journal_md=content,
    )
    conn = get_global_db()
    persist_run(conn, run)

    print(f"✓ Parsed {len(records)} turns")
    print(
        f"✓ Classified: {decisions} decisions, {corrections} corrections, "
        f"{pattern_count} patterns, {blockers} blockers"
    )
    print(f"✓ Patterns persisted: {pattern_count}")
    print(f"✓ Journal written: {journal_path}")
    print(f"✓ Run persisted: {session_id}")


def main() -> None:
    """CLI entry point for python -m raise_cli.distillation.agent."""
    from raise_cli.distillation.llm_classifier import BACKENDS
    from raise_cli.telemetry.session_tokens import find_current_session_jsonl

    parser = argparse.ArgumentParser(
        description="Post-session distillation agent — extracts signals from JSONL transcripts."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--session", type=Path, help="Path to a specific JSONL file")
    group.add_argument(
        "--project", type=Path, help="Project root — uses most recent JSONL"
    )
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=None,
        help=(
            "LLM classifier backend (default: RAISE_DISTILLATION_BACKEND env var, "
            "then 'deepseek'). No implicit fallback between backends."
        ),
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        default=False,
        help="Enable LLM classification (overrides RAISE_DISTILLATION_LLM env var)",
    )
    parser.add_argument(
        "--two-stage",
        action="store_true",
        default=False,
        dest="two_stage",
        help=(
            "Enable two-stage CoT verification pass on INSIGHT candidates "
            "(overrides RAISE_DISTILLATION_TWO_STAGE env var). "
            "Requires --llm or RAISE_DISTILLATION_LLM=1."
        ),
    )
    args = parser.parse_args()

    if args.project:
        jsonl = find_current_session_jsonl(args.project)
        if jsonl is None:
            print(f"ERROR: No JSONL found for project {args.project}")
            raise SystemExit(1)
    else:
        jsonl = args.session

    use_llm = args.llm or None  # None = defer to env var
    two_stage = args.two_stage or None  # None = defer to env var
    asyncio.run(
        distill(jsonl, use_llm=use_llm, backend=args.backend, two_stage=two_stage)
    )


if __name__ == "__main__":
    main()
