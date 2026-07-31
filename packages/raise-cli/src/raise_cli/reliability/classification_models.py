"""Pydantic models for TargetClassifier — inference classification (RAISE-11491).

Core types:
- BugRecord: minimal bug signal for classification (read from Jira)
- TargetClassification: classifier output for one bug
- CostEstimate: dry-run cost projection for a batch
- ClassifierConfig: classifier configuration with BYOK extension hook

The ``provider`` field on ClassifierConfig is the BYOK extension hook (RAISE-11585):
adding a second provider (e.g. "openrouter") only requires adding a new LlmProvider
implementation and branching in TargetClassifier.__init__ — no other changes.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.reliability.models import Target

__all__ = [
    "BugRecord",
    "ClassifierConfig",
    "CostEstimate",
    "TargetClassification",
]


class BugRecord(BaseModel):
    """Minimal bug signal for classification (read-only from Jira)."""

    key: str
    """Jira issue key (e.g. "RAISE-1234")."""

    title: str
    """Issue summary / title."""

    description: str = ""
    """Issue description (Jira body). Empty when not available."""

    origin: str | None = None
    """cf13269 if already set in Jira; None means "needs classification"."""

    bug_type: str | None = None
    """cf13267 if already set in Jira; None means "needs classification"."""


class TargetClassification(BaseModel):
    """Classifier output for one bug.

    ``confidence`` is constrained to [0.0, 1.0) — never exactly 1.0 (trampa 5:
    LLM overconfidence). A confidence ≤ threshold yields target=UNKNOWN with
    confidence=0.0 rather than an invented classification.
    """

    bug_key: str
    """Jira issue key (matches BugRecord.key)."""

    target: Target
    """Change target: PRODUCT/TEST/CONFIG/DOCS/OTHER/UNKNOWN."""

    origin: str
    """cf13269 vocab: Code/Design/Integration/Environment/Requirements."""

    bug_type: str
    """cf13267 vocab: Logic/State/Interface/Performance/Security."""

    confidence: float = Field(ge=0.0, lt=1.0)
    """Classification confidence in [0.0, 1.0). Never 1.0."""

    rationale: str
    """Audit trail — explains the classification decision."""


class CostEstimate(BaseModel):
    """Dry-run cost projection for a classify_batch() call.

    All token/cost values are estimates; accuracy target is ±20% of actual
    (validated via count_tokens per prompt, applying Batch API -50% discount).
    """

    bug_count: int
    """Number of bugs included in the estimate."""

    estimated_input_tokens: int
    """Total estimated input tokens across all prompts."""

    estimated_output_tokens: int
    """Total estimated output tokens across all responses."""

    estimated_usd: float
    """Batch-discounted cost estimate in USD."""

    model: str
    """Model used for the estimate."""

    cache_hits: int = 0
    """Bugs served from cache — excluded from cost estimate."""


class ClassifierConfig(BaseModel):
    """Configuration for TargetClassifier.

    The ``provider`` field is the BYOK extension hook (RAISE-11585): setting it
    to "openrouter" (or any future value) selects the matching LlmProvider
    implementation without changing TargetClassifier internals.
    """

    model: str = "claude-opus-4-8"
    """Claude model ID. Default: claude-opus-4-8 (required for Design accuracy)."""

    batch_size: int = 25
    """Bugs per Batch API request. Anthropic limit: 100k requests/batch."""

    confidence_threshold: float = 0.6
    """Minimum confidence to accept a classification; below → UNKNOWN."""

    api_key: str | None = None
    """Explicit API key. Overrides env/hermes resolver chain (D2)."""

    cache_dir: Path | None = None
    """Directory for disk cache. None → no caching."""

    provider: str = "anthropic"
    """LLM provider selector — BYOK extension hook (RAISE-11585).
    "anthropic" → AnthropicProvider; future: "openrouter" → OpenRouterProvider.
    """
