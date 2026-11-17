"""Typed models for the commit-stream defect/rework classifier (RAISE-11187).

Reliability/Quality lens over the commit stream: parse conventional-commit
metadata, classify each commit, and aggregate defect/rework rates. Heuristic by
design — see ``DefectClass`` for the honest caveats.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CommitCategory = Literal["feat", "fix", "bug", "test", "docs", "chore", "other"]
"""Conventional-commit category derived from the subject prefix."""

DefectClass = Literal["rework_in_process", "escaped", "n/a"]
"""Heuristic defect classification for fix/bug commits.

- ``rework_in_process``: a fix/bug commit that carries an in-process rework
  marker (architecture/quality review remediation, CI/gate/lint/type fixes).
  These are corrections caught *before* shipping — healthy, expected churn.
- ``escaped``: a fix/bug commit with no in-process marker — a *candidate*
  escaped defect (touched code with no sign it was caught in review/CI).
  This is a heuristic signal, not a confirmed escape.
- ``n/a``: non-fix commits (feat/test/docs/chore/other).
"""


class CommitRecord(BaseModel):
    """One parsed commit from ``git log`` (no merge commits)."""

    sha: str
    type: CommitCategory
    scope: str | None = None
    subject: str
    ticket_refs: list[str] = Field(default_factory=list)
    author: str = ""
    date: datetime | None = None


class CommitClassification(BaseModel):
    """Classifier verdict for a single commit."""

    category: CommitCategory
    traceable: bool
    defect_class: DefectClass


class WindowMetrics(BaseModel):
    """Defect/rework metrics for one time window (or the whole range)."""

    label: str
    total: int = 0
    fix_count: int = 0
    bug_count: int = 0
    rework_count: int = 0
    escaped_count: int = 0

    @property
    def fix_rate(self) -> float:
        """Share of commits that are fix-type."""
        return self.fix_count / self.total if self.total else 0.0

    @property
    def bug_rate(self) -> float:
        """Share of commits that are bug-type."""
        return self.bug_count / self.total if self.total else 0.0

    @property
    def rework_rate(self) -> float:
        """Share of commits classified as in-process rework."""
        return self.rework_count / self.total if self.total else 0.0

    @property
    def escaped_rate(self) -> float:
        """Share of commits classified as candidate escaped defects."""
        return self.escaped_count / self.total if self.total else 0.0


class DefectRateReport(BaseModel):
    """Top-level report returned by :func:`defect_rate`."""

    branch: str
    since_days: int
    overall: WindowMetrics
    windows: list[WindowMetrics] = Field(default_factory=list)


# ── Jira-taxonomy enrichment (RAISE-11207) ──────────────────────────────────

UNCATEGORIZED = "uncategorized"
"""Bucket label for fix/bug commits whose Jira ticket lacks the field, is not a
Bug-type issue, or has no resolvable ticket ref. Must never crash the report —
the dominant share of the stream is uncategorized."""

GroupBy = Literal["origin", "type"]
"""Dimensions the defect rate can be grouped by, sourced from Jira custom fields:
``origin`` = cf[13269] (Bug Origin), ``type`` = cf[13267] (Bug Type)."""


class FieldBucket(BaseModel):
    """Defect counts for one value of a grouped dimension (e.g. Origin=Design)."""

    value: str
    fix_bug_count: int = 0
    """fix/bug commits whose ticket carries this field value."""


class FieldGroupReport(BaseModel):
    """Defect rate grouped by a single Jira taxonomy dimension.

    ``coverage`` = share of fix/bug commits that resolved to a categorized value
    (i.e. a Bug-type ticket with the field populated). The remainder lands in the
    :data:`UNCATEGORIZED` bucket.
    """

    dimension: GroupBy
    total_fix_bug: int = 0
    categorized: int = 0
    buckets: list[FieldBucket] = Field(default_factory=list)

    @property
    def coverage(self) -> float:
        """Share of fix/bug commits that carry a categorized field value."""
        return self.categorized / self.total_fix_bug if self.total_fix_bug else 0.0


class CrossCell(BaseModel):
    """One Origin×Type cell of the cross-tabulation."""

    origin: str
    type: str
    fix_bug_count: int = 0


class EnrichedDefectReport(BaseModel):
    """Defect rate enriched with Jira taxonomy (Origin, Type, Origin×Type).

    Aggregates only fix/bug commits — those are the defect signal the Jira bug
    taxonomy describes. Non-fix commits are excluded from ``total_fix_bug``.
    """

    branch: str
    since_days: int
    total_fix_bug: int = 0
    by_origin: FieldGroupReport | None = None
    by_type: FieldGroupReport | None = None
    cross: list[CrossCell] = Field(default_factory=list)
