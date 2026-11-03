"""Reliability/Quality lens over the commit stream (RAISE-11187, RAISE-11207)."""

from __future__ import annotations

from raise_cli.quality.classifier import (
    classify,
    defect_rate,
    parse_commits,
    parse_git_log,
    resolve_branch,
)
from raise_cli.quality.enrichment import (
    BugFields,
    JiraFieldLookup,
    adapter_field_lookup,
    enrich_commits,
    fields_from_metadata,
)
from raise_cli.quality.models import (
    CommitClassification,
    CommitRecord,
    CrossCell,
    DefectRateReport,
    EnrichedDefectReport,
    FieldBucket,
    FieldGroupReport,
    WindowMetrics,
)

__all__ = [
    "BugFields",
    "CommitClassification",
    "CommitRecord",
    "CrossCell",
    "DefectRateReport",
    "EnrichedDefectReport",
    "FieldBucket",
    "FieldGroupReport",
    "JiraFieldLookup",
    "WindowMetrics",
    "adapter_field_lookup",
    "classify",
    "defect_rate",
    "enrich_commits",
    "fields_from_metadata",
    "parse_commits",
    "parse_git_log",
    "resolve_branch",
]
