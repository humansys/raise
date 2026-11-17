"""Evaluation result models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvalResult(BaseModel):
    """Result of an evaluation run."""

    suite: str
    metrics: dict[str, float] = Field(default_factory=dict)
    per_query: dict[str, dict[str, float]] = Field(default_factory=dict)
    num_queries: int = 0
    corpus_hash: str = ""
    thresholds: dict[str, float] | None = None
    ci: dict[str, tuple[float, float]] | None = None


class TuningResult(BaseModel):
    """Result of a single weight combination evaluation."""

    weights: tuple[float, ...]
    metrics: dict[str, float] = Field(default_factory=dict)
