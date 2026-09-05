"""AgentTelemetryAdapter Protocol — cross-runtime telemetry normalization.

Aspect transversal (ADR-062 extended): cualquier módulo que necesite
métricas de sesión de agente consume RawSessionWindow vía este Protocol,
no formatos nativos de runtime.

Lives in raise-core alongside RaiAgentRuntime so any package can depend
on the contract without coupling to raise-cli.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel


class ModelCostBreakdown(BaseModel):
    """Per-model usage and cost breakdown (runtime-agnostic)."""

    model: str
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write: int = 0
    cache_read: int = 0
    cost_usd: float = 0.0


class RawSessionWindow(BaseModel):
    """Normalized session data for a temporal window."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    by_model: list[ModelCostBreakdown] = []
    tool_calls: int = 0
    tool_failures: int = 0
    edit_reverts: int = 0
    gate_fail_streak: int = 0


@runtime_checkable
class AgentTelemetryAdapter(Protocol):
    """Contract for extracting session metrics from any agent runtime."""

    @property
    def runtime_name(self) -> str:
        """Runtime identifier (e.g. 'claude_code', 'hermes', 'codex_cli')."""
        ...

    def find_session_data(self, project_path: Path) -> Path | None:
        """Locate the active session data source (JSONL, SQLite, API, etc.)."""
        ...

    def extract_window(
        self,
        source: Path,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> RawSessionWindow:
        """Extract normalized metrics for a temporal window."""
        ...
