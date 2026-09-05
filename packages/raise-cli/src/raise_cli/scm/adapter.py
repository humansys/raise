"""ScmAdapter Protocol, provider factory, and CI polling helper (RAISE-16773).

This is the single dispatch point for merge-request lifecycle operations. It
replaces ``raise_cli.adapters.scm_adapter.RaiseServerScmAdapter``, which S6
(RAISE-16777) removes; nothing here may import it (epic design D1/D3).

Three pieces live here:

``ScmAdapter``
    The Protocol from ADR-2026-08-29. Four provider classes conform
    structurally — two real (GitLab, GitHub), two stubs awaiting RAISE-16775.

``from_manifest()``
    Provider resolution. Delegates to ``resolve_scm`` (D9): the manifest has
    exactly one read path, and adding a second here is how the two would drift.
    Fails closed when the provider is unresolved or unknown — absence is not a
    guess (RAISE-16561). The backward-compatible ``gitlab`` default lives at
    the CLI edge (``rai scm create-mr``), not in this library, so a genuinely
    misconfigured repository cannot silently open MRs on the wrong provider.

``wait_for_ci_status()``
    Provider-agnostic polling around the Protocol's single-shot status read
    (D-S3-5). ``sleep`` and ``clock`` are injectable so the 30-minute default
    timeout is testable without a 30-minute test.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from raise_cli.project_config.branches import resolve_scm

CiStatus = Literal["pending", "running", "success", "failed"]
"""CI verdict, normalised across providers.

Only ``success`` is permission to proceed. Every provider state that is neither
clearly-passing nor clearly-in-progress maps to ``failed`` — see the mapping
tables in the GitLab and GitHub adapters.
"""

TERMINAL_STATUSES: frozenset[str] = frozenset({"success", "failed"})

DEFAULT_CI_TIMEOUT_SECONDS = 1800.0
DEFAULT_CI_POLL_INTERVAL_SECONDS = 30.0


class ScmError(Exception):
    """Base class for every failure originating in this package."""


class ScmConfigError(ScmError):
    """The SCM provider could not be resolved, or is not one we implement."""


class ScmCommandError(ScmError):
    """The provider CLI was missing, failed, timed out, or returned junk."""


@runtime_checkable
class ScmAdapter(Protocol):
    """Provider-agnostic merge-request operations (ADR-2026-08-29).

    Deliberately three methods. ``create_mr`` and ``get_mr_ci_status`` are used
    by ``rai-mr-create`` (S3); ``merge_mr`` exists now, unused, because S4
    consumes it and a Protocol that grows per-caller is not a contract.

    Naming is GitLab's ("merge request") for all providers. The GitHub adapter
    is the only place that knows to say ``pr`` instead — PAT-129.
    """

    def create_mr(
        self,
        *,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
    ) -> str:
        """Open a merge request and return its URL."""
        ...

    def merge_mr(self, *, mr_url: str, delete_source_branch: bool = True) -> None:
        """Merge an open merge request."""
        ...

    def get_mr_ci_status(self, *, mr_url: str) -> CiStatus:
        """Read the merge request's current CI verdict. One shot, no polling."""
        ...


def _provider_registry() -> dict[str, type]:
    """Import adapters lazily to keep this module importable in isolation."""
    from raise_cli.scm.azdo_adapter import AzureDevOpsAdapter
    from raise_cli.scm.bitbucket_adapter import BitbucketAdapter
    from raise_cli.scm.github_adapter import GitHubAdapter
    from raise_cli.scm.gitlab_adapter import GitLabAdapter

    return {
        "gitlab": GitLabAdapter,
        "github": GitHubAdapter,
        "azuredevops": AzureDevOpsAdapter,
        "bitbucket": BitbucketAdapter,
    }


def from_manifest(project: Path | None = None) -> ScmAdapter:
    """Build the adapter for the project's configured SCM provider.

    Args:
        project: Repository root. Defaults to the current working directory.

    Returns:
        An adapter conforming to :class:`ScmAdapter`.

    Raises:
        ScmConfigError: ``branches.scm`` is unset, or names a provider that has
            no adapter. Both messages name the four accepted values, because
            the developer reading them is looking at a YAML file.
    """
    registry = _provider_registry()
    accepted = ", ".join(sorted(registry))

    raw = resolve_scm(project if project is not None else Path.cwd())
    if raw is None or not raw.strip():
        raise ScmConfigError(
            "No SCM provider configured: set branches.scm in .raise/manifest.yaml "
            f"(or the RAISE_SCM environment variable) to one of: {accepted}."
        )

    provider = raw.strip().lower()
    adapter_cls = registry.get(provider)
    if adapter_cls is None:
        raise ScmConfigError(
            f"Unknown SCM provider {raw.strip()!r} — accepted values are: {accepted}."
        )
    adapter: ScmAdapter = adapter_cls()
    return adapter


def wait_for_ci_status(
    adapter: ScmAdapter,
    *,
    mr_url: str,
    timeout_seconds: float = DEFAULT_CI_TIMEOUT_SECONDS,
    poll_interval_seconds: float = DEFAULT_CI_POLL_INTERVAL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> CiStatus:
    """Poll ``adapter.get_mr_ci_status`` until it is terminal or time runs out.

    Args:
        adapter: Any conforming adapter.
        mr_url: The merge request to watch.
        timeout_seconds: Give up after this long. Default 30 minutes.
        poll_interval_seconds: Wait between reads.
        sleep: Injected for tests; must block for the given seconds.
        clock: Injected for tests; must be monotonic.

    Returns:
        The terminal status, or ``"failed"`` if the timeout expired first.
        Fail-closed on purpose: CI that never finished has validated nothing,
        and reporting ``pending`` here would let a caller treat "unknown" as
        "not yet a problem" (D-S3-5).
    """
    deadline = clock() + timeout_seconds

    while True:
        status = adapter.get_mr_ci_status(mr_url=mr_url)
        if status in TERMINAL_STATUSES:
            return status
        if clock() + poll_interval_seconds > deadline:
            return "failed"
        sleep(poll_interval_seconds)
