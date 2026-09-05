"""SCM provider adapters — merge request lifecycle (RAISE-16770).

This package is the home of the ``ScmAdapter`` surface: the provider-specific
half of creating, merging, and status-checking merge requests. It replaces the
server-backed ``raise_cli.adapters.scm_adapter.RaiseServerScmAdapter``, which
S6 removes.

What lives here as of S3 (RAISE-16773)
--------------------------------------
The ``ScmAdapter`` Protocol from ADR-2026-08-29, the GitLab and GitHub
implementations, the ``from_manifest()`` factory, and the ``wait_for_ci_status``
polling helper — plus the two unimplemented-provider stubs S1 left behind.
``branches.scm`` accepts ``azuredevops`` and ``bitbucket``, which makes those
providers selectable, and a selectable provider needs something behind it that
fails legibly; RAISE-16775 replaces both stubs with real adapters.

Because the stubs were written against the ADR signatures, S3 introduced the
Protocol and all four classes conformed structurally with no edit to either.

Shared namespace
----------------
The DORA mining modules from RAISE-11144 also land in ``raise_cli.scm``. Keep
the two export groups separate in this file — adapters here, mining there — so
neither story's merge silently swallows the other's exports.
"""

from __future__ import annotations

from raise_cli.scm.adapter import (
    DEFAULT_CI_POLL_INTERVAL_SECONDS,
    DEFAULT_CI_TIMEOUT_SECONDS,
    CiStatus,
    ScmAdapter,
    ScmCommandError,
    ScmConfigError,
    ScmError,
    from_manifest,
    wait_for_ci_status,
)
from raise_cli.scm.azdo_adapter import AzureDevOpsAdapter
from raise_cli.scm.bitbucket_adapter import BitbucketAdapter
from raise_cli.scm.conflict_rules import (
    ConflictConfigError,
    ConflictResolutionConfig,
    ConflictResolutionError,
    ConflictRule,
    GitStateError,
    ResolutionReport,
    load_config,
    match_rule,
    resolve_conflicts,
)
from raise_cli.scm.github_adapter import GitHubAdapter
from raise_cli.scm.gitlab_adapter import GitLabAdapter

__all__ = [
    # --- MR lifecycle adapters (RAISE-16770) ---
    "AzureDevOpsAdapter",
    "BitbucketAdapter",
    "DEFAULT_CI_POLL_INTERVAL_SECONDS",
    "DEFAULT_CI_TIMEOUT_SECONDS",
    "CiStatus",
    "GitHubAdapter",
    "GitLabAdapter",
    "ScmAdapter",
    "ScmCommandError",
    "ScmConfigError",
    "ScmError",
    "from_manifest",
    "wait_for_ci_status",
    # --- Merge-conflict resolution policy (RAISE-16772, S2) ---
    # Separate group on purpose: this half has no provider and no server
    # dependency, so S6's removal of RaiseServerScmAdapter must not touch it.
    "ConflictConfigError",
    "ConflictResolutionConfig",
    "ConflictResolutionError",
    "ConflictRule",
    "GitStateError",
    "ResolutionReport",
    "load_config",
    "match_rule",
    "resolve_conflicts",
]
