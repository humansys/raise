"""Jira-taxonomy enrichment for the commit-stream classifier (RAISE-11207).

The base classifier (RAISE-11187) reads only what ``git log`` exposes. This
layer joins each fix/bug commit's ``RAISE-NNNN`` ticket ref to the bug's Jira
taxonomy custom fields and aggregates the defect rate by **Origin** (cf[13269]),
**Bug Type** (cf[13267]), and the **Origin×Type** cross.

Bug-data discovery motivated the cut: Origin is split (Design ≈45% / Code ≈44%)
and Bug Type Logic dominates (~33%) — flat fix-rate hides *where* defects come
from. Grouping by taxonomy makes that visible.

Design constraints (from the story):

- **Adapter, not raw Jira.** Custom fields are read through the resolved backlog
  adapter (``IssueDetail.metadata``), never raw REST / MCP / env creds. See
  :func:`adapter_field_lookup`.
- **Bug-type only.** Stories/epics don't carry these fields; non-Bug issues and
  missing fields fall into the :data:`~raise_cli.quality.models.UNCATEGORIZED`
  bucket and must never crash the report.
- **Offline-testable.** The network lookup is injected as a
  :class:`JiraFieldLookup`; tests pass a dict-backed stub. No live calls in tests.
- **Network-frugal.** :func:`enrich_commits` de-duplicates ticket refs before
  looking anything up, so each ticket is fetched at most once per run.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from raise_cli.quality.models import (
    CommitRecord,
    CrossCell,
    EnrichedDefectReport,
    FieldBucket,
    FieldGroupReport,
    GroupBy,
)

# Jira custom-field ids for the RAISE bug taxonomy (org-calibrated, RAISE-11207).
CF_ORIGIN = "customfield_13269"
CF_BUG_TYPE = "customfield_13267"
CF_SEVERITY = "customfield_12090"

# Issue keys we can join to Jira (RAISE project). Mirrors the classifier's
# ticket regex but anchored to RAISE- so we never fetch a story/epic shorthand.
_RAISE_KEY_RE = re.compile(r"RAISE-\d+")

_BUG_ISSUE_TYPES = frozenset({"bug", "defect"})


class BugFields(BaseModel):
    """Normalized Jira taxonomy for one bug ticket.

    ``None`` on any attribute means the field was absent/empty. A non-Bug issue
    yields ``is_bug=False`` and all-``None`` fields, which the aggregator treats
    as uncategorized.
    """

    model_config = ConfigDict(frozen=True)

    origin: str | None
    bug_type: str | None
    severity: str | None
    is_bug: bool


class JiraFieldLookup(Protocol):
    """Maps a Jira issue key to its bug taxonomy, or ``None`` if unresolvable.

    Implementations are injected so the aggregation is unit-testable offline.
    The production implementation is :func:`adapter_field_lookup`.
    """

    def __call__(self, key: str) -> BugFields | None:
        """Resolve ``key`` to its bug taxonomy, or ``None`` if unresolvable."""
        ...


def _unwrap(value: Any) -> str | None:
    """Normalize a raw Jira custom-field value to a display string.

    Select fields arrive as ``{"value": "Design"}``; cascading selects nest a
    ``child``; scalars arrive bare. Returns ``None`` for empty/absent values.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        inner = value.get("value")
        return str(inner) if inner not in (None, "") else None
    text = str(value).strip()
    return text or None


def fields_from_metadata(issue_type: str, metadata: dict[str, Any]) -> BugFields:
    """Build :class:`BugFields` from an ``IssueDetail``'s type + metadata.

    ``metadata`` is the raw ``customfield_*`` map surfaced by the Jira adapter.
    Non-Bug issue types yield ``is_bug=False`` with no fields — the caller's
    aggregator counts those as uncategorized.
    """
    is_bug = issue_type.strip().lower() in _BUG_ISSUE_TYPES
    if not is_bug:
        return BugFields(origin=None, bug_type=None, severity=None, is_bug=False)
    return BugFields(
        origin=_unwrap(metadata.get(CF_ORIGIN)),
        bug_type=_unwrap(metadata.get(CF_BUG_TYPE)),
        severity=_unwrap(metadata.get(CF_SEVERITY)),
        is_bug=True,
    )


def adapter_field_lookup(adapter: Any) -> JiraFieldLookup:
    """Build a :class:`JiraFieldLookup` backed by a resolved backlog adapter.

    Reads custom fields through the canonical adapter path
    (``adapter.get_issue(key).metadata``) — no raw Jira REST, no MCP, no direct
    env credentials. The adapter is resolved by the caller via
    ``raise_cli.adapters.resolve.resolve_pm_adapter`` (honoring the Canonical
    Resolver guardrail). Any per-ticket lookup failure degrades to ``None``
    (counted as uncategorized) rather than aborting the whole report.

    Args:
        adapter: A resolved ``ProjectManagementAdapter`` (sync-wrapped).

    Returns:
        A callable taking an issue key and returning :class:`BugFields` or
        ``None``.
    """

    def _lookup(key: str) -> BugFields | None:
        try:
            detail = adapter.get_issue(key)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return None
        return fields_from_metadata(detail.issue_type, detail.metadata)

    return _lookup


def _fix_bug_keys(commits: list[CommitRecord]) -> tuple[int, list[str]]:
    """Return (#fix/bug commits, de-duplicated RAISE keys among them).

    Each commit may carry multiple refs; we collect every RAISE-key once so the
    network lookup runs at most once per ticket. Commits without a RAISE key are
    still counted in the total (they become uncategorized).
    """
    total = 0
    keys: set[str] = set()
    for commit in commits:
        if commit.type not in {"fix", "bug"}:
            continue
        total += 1
        for ref in commit.ticket_refs:
            keys.update(_RAISE_KEY_RE.findall(ref))
    return total, sorted(keys)


def resolve_bug_fields(
    keys: list[str], lookup: JiraFieldLookup
) -> dict[str, BugFields | None]:
    """Resolve each key once via ``lookup`` into a cache dict."""
    return {key: lookup(key) for key in keys}


def _commit_value(
    commit: CommitRecord,
    resolved: dict[str, BugFields | None],
    attr: str,
) -> str | None:
    """Pick the taxonomy value (origin/bug_type) for one fix/bug commit.

    A commit may reference several tickets; we take the first that resolves to a
    Bug with the requested field populated. Returns ``None`` (→ uncategorized)
    when nothing resolves.
    """
    for ref in commit.ticket_refs:
        for key in _RAISE_KEY_RE.findall(ref):
            fields = resolved.get(key)
            if fields is not None and fields.is_bug:
                value = getattr(fields, attr)
                if value is not None:
                    return value
    return None


def _group_report(
    commits: list[CommitRecord],
    resolved: dict[str, BugFields | None],
    dimension: GroupBy,
    total_fix_bug: int,
) -> FieldGroupReport:
    attr = "origin" if dimension == "origin" else "bug_type"
    counts: Counter[str] = Counter()
    categorized = 0
    for commit in commits:
        if commit.type not in {"fix", "bug"}:
            continue
        value = _commit_value(commit, resolved, attr)
        if value is None:
            continue
        counts[value] += 1
        categorized += 1
    buckets = [
        FieldBucket(value=value, fix_bug_count=count)
        for value, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return FieldGroupReport(
        dimension=dimension,
        total_fix_bug=total_fix_bug,
        categorized=categorized,
        buckets=buckets,
    )


def _cross_cells(
    commits: list[CommitRecord], resolved: dict[str, BugFields | None]
) -> list[CrossCell]:
    """Origin×Type cross-tab over fix/bug commits with both fields resolved."""
    counts: Counter[tuple[str, str]] = Counter()
    for commit in commits:
        if commit.type not in {"fix", "bug"}:
            continue
        origin = _commit_value(commit, resolved, "origin")
        bug_type = _commit_value(commit, resolved, "bug_type")
        if origin is None or bug_type is None:
            continue
        counts[(origin, bug_type)] += 1
    return [
        CrossCell(origin=origin, type=bug_type, fix_bug_count=count)
        for (origin, bug_type), count in sorted(
            counts.items(), key=lambda kv: (-kv[1], kv[0])
        )
    ]


def enrich_commits(
    commits: list[CommitRecord],
    lookup: JiraFieldLookup,
    *,
    branch: str,
    since_days: int,
    by: list[GroupBy],
) -> EnrichedDefectReport:
    """Aggregate defect rate over fix/bug commits, grouped by Jira taxonomy.

    Args:
        commits: Parsed :class:`~raise_cli.quality.models.CommitRecord` list.
        lookup: Injected Jira field lookup (mockable offline).
        branch: Branch the commits came from (report header).
        since_days: Look-back window (report header).
        by: Dimensions to group by — any of ``"origin"``, ``"type"``. The
            Origin×Type cross is emitted whenever both are requested.

    Returns:
        An :class:`EnrichedDefectReport`. Uncategorized fix/bug commits (no
        resolvable Bug ticket / missing field) are reflected as the gap between
        ``total_fix_bug`` and each group's ``categorized`` — never dropped,
        never raised.
    """
    total_fix_bug, keys = _fix_bug_keys(commits)
    resolved = resolve_bug_fields(keys, lookup)

    report = EnrichedDefectReport(
        branch=branch, since_days=since_days, total_fix_bug=total_fix_bug
    )
    if "origin" in by:
        report.by_origin = _group_report(commits, resolved, "origin", total_fix_bug)
    if "type" in by:
        report.by_type = _group_report(commits, resolved, "type", total_fix_bug)
    if "origin" in by and "type" in by:
        report.cross = _cross_cells(commits, resolved)
    return report


__all__ = [
    "CF_BUG_TYPE",
    "CF_ORIGIN",
    "CF_SEVERITY",
    "BugFields",
    "JiraFieldLookup",
    "adapter_field_lookup",
    "enrich_commits",
    "fields_from_metadata",
    "resolve_bug_fields",
]
