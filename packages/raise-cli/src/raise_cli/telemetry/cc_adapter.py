"""ClaudeCodeTelemetryAdapter — CC-specific implementation of AgentTelemetryAdapter.

Wraps existing scan_single_session + find_current_session_jsonl to produce
RawSessionWindow. Thin adapter — no new parsing logic.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from raise_core.runtime.telemetry_adapter import (
    ModelCostBreakdown,
    RawSessionWindow,
)


class ClaudeCodeTelemetryAdapter:
    """Extract session metrics from Claude Code JSONL logs."""

    @property
    def runtime_name(self) -> str:
        """Return 'claude_code'."""
        return "claude_code"

    def find_session_data(self, project_path: Path) -> Path | None:
        """Locate the most recent CC JSONL in ~/.claude/projects/."""
        from raise_cli.telemetry.session_tokens import find_current_session_jsonl

        return find_current_session_jsonl(project_path)

    def extract_window(
        self,
        source: Path,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> RawSessionWindow:
        """Extract metrics from CC JSONL for the given time window."""
        from raise_cli.telemetry.cost_report import scan_single_session

        report = scan_single_session(source, since=since, until=until)
        return RawSessionWindow(
            input_tokens=sum(m.input_tokens for m in report.models),
            output_tokens=sum(m.output_tokens for m in report.models),
            cost_usd=report.total_cost_usd,
            by_model=[
                ModelCostBreakdown(
                    model=m.model,
                    calls=m.calls,
                    input_tokens=m.input_tokens,
                    output_tokens=m.output_tokens,
                    cache_write=m.cache_write,
                    cache_read=m.cache_read,
                    cost_usd=m.cost_usd,
                )
                for m in report.models
            ],
            tool_calls=0,
            tool_failures=round(report.tool_fail_ratio * 100)
            if report.tool_fail_ratio is not None
            else 0,
            edit_reverts=report.edit_revert_files,
            gate_fail_streak=report.max_gate_fail_streak,
        )


class NullTelemetryAdapter:
    """Fail-open adapter for runtimes without a registered adapter."""

    @property
    def runtime_name(self) -> str:
        """Return 'unknown'."""
        return "unknown"

    def find_session_data(self, project_path: Path) -> Path | None:
        """Return None — no data available for unknown runtimes."""
        return None

    def extract_window(
        self,
        source: Path,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> RawSessionWindow:
        """Return zeros — fail-open for unknown runtimes."""
        return RawSessionWindow()
