"""Runtime contracts: RunConfig and RunResult.

Shared between pipeline and daemon — no SDK imports here.

Story: S1064.4 — LLM Phase Executor
Epic: E1064 — Pipeline Engine Core
Extracted to raise-core: RAISE-1430
"""

from typing import Any, Literal

from pydantic import BaseModel


class RunConfig(BaseModel):
    """Input contract for agent dispatch.

    Balanced surface: covers daemon needs (S2.3) + pipeline needs (S1064.4).
    All fields except ``prompt`` are optional for backward compatibility.
    """

    prompt: str
    content_blocks: list[dict[str, Any]] | None = None
    """Multimodal content blocks (images + text). When present,
    runtime uses AsyncIterable mode to send structured content."""
    session_id: str | None = None
    system_prompt: str | None = None
    permission_mode: Literal["default", "acceptEdits", "bypassPermissions"] | None = (
        None
    )
    max_turns: int | None = None
    skills: list[str] | None = None
    memory_paths: list[str] | None = None
    sensitive_patterns: list[str] | None = None
    cwd: str | None = None
    # S1064.4 pipeline additions — backward compatible
    max_budget_usd: float | None = None
    model: str | None = None
    # S1.1 (RAISE-15302) tenant identity for messaging channels — optional,
    # backward compatible by construction (all fields except prompt are optional)
    tenant_id: str | None = None
    agent_id: str | None = None


class RunResult(BaseModel):
    """Result from an agent run, including session and usage metrics.

    Migrated from dataclass to Pydantic for consistency with RunConfig
    (AR Q2, S1064.4).
    """

    session_id: str | None = None
    input_tokens: int = 0
    # S1064.4 pipeline additions — backward compatible
    output_tokens: int = 0
    cost_usd: float = 0.0
    num_turns: int = 0
    output_text: str = ""
    stop_reason: str | None = None
    """SDK-provided termination reason (e.g. 'budget_exceeded', 'max_turns').
    None if the agent completed normally. AR Q4: prefer SDK-authoritative
    reason over heuristic comparison."""
