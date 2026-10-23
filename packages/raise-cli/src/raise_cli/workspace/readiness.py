"""Workspace readiness models and pure evaluator — S14897.1 / RAISE-14900.

Generic workspace readiness contract. Does not encode git or worktree
assumptions. Specific policies (e.g. git worktree) live near their own
provisioning code and compose checks from this module.

Public API:
    WorkspaceReadinessFinding
    WorkspaceReadinessPolicy
    WorkspaceReadinessReport
    evaluate_workspace_readiness
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field


class WorkspaceReadinessFinding(BaseModel, frozen=True):
    """A single readiness finding emitted by a check function.

    Attributes:
        code:      Stable machine-readable snake_case identifier.
        message:   Human-readable description of the issue.
        severity:  "required" blocks readiness; "advisory" is informational only.
        path:      Optional filesystem path the finding relates to.
        evidence:  Optional structured evidence dict for downstream consumers.
    """

    code: str = Field(description="Stable machine-readable finding code (snake_case).")
    message: str = Field(description="Human-readable description.")
    severity: Literal["required", "advisory"] = Field(
        description="'required' blocks readiness; 'advisory' is informational."
    )
    path: Path | None = Field(default=None, description="Related filesystem path.")
    evidence: dict[str, Any] | None = Field(
        default=None, description="Structured evidence for downstream consumers."
    )


class WorkspaceReadinessPolicy(BaseModel):
    """A named collection of check callables that together define readiness.

    Each check is a callable of the form:
        check(path: Path) -> list[WorkspaceReadinessFinding]

    Policies are workspace-generic. Git-worktree-specific policy lives in
    raise_cli.worktree.provision.git_worktree_readiness_policy().

    Attributes:
        policy_id: Stable identifier for this policy (e.g. "git-worktree-v1").
        checks:    Ordered list of check callables.
    """

    model_config = {"arbitrary_types_allowed": True}

    policy_id: str = Field(description="Stable policy identifier.")
    checks: list[Callable[[Path], list[WorkspaceReadinessFinding]]] = Field(
        default_factory=list,
        description="Ordered list of check callables.",
    )


class WorkspaceReadinessReport(BaseModel):
    """Result of evaluating a workspace against a readiness policy.

    Attributes:
        workspace_path: Absolute path to the evaluated workspace.
        policy_id:      Policy used for evaluation.
        findings:       All findings (required + advisory) from all checks.
        is_ready:       True iff there are no required findings.
        required_findings: Filtered view of severity="required" findings.
    """

    workspace_path: Path = Field(description="Evaluated workspace path.")
    policy_id: str = Field(description="Policy identifier used for evaluation.")
    findings: list[WorkspaceReadinessFinding] = Field(
        default_factory=list,
        description="All findings from all checks.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_ready(self) -> bool:
        """True iff there are no required findings."""
        return all(f.severity != "required" for f in self.findings)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def required_findings(self) -> list[WorkspaceReadinessFinding]:
        """Required findings only (those that block readiness)."""
        return [f for f in self.findings if f.severity == "required"]


def evaluate_workspace_readiness(
    path: Path,
    policy: WorkspaceReadinessPolicy,
) -> WorkspaceReadinessReport:
    """Evaluate workspace readiness by running all checks in the policy.

    This function is pure and side-effect free: it reads the filesystem but
    never writes, never invokes subprocesses, and is deterministic for a
    given filesystem snapshot.

    Args:
        path:   Workspace root directory to evaluate.
        policy: Policy defining which checks to run.

    Returns:
        A WorkspaceReadinessReport aggregating all findings from all checks.
    """
    all_findings: list[WorkspaceReadinessFinding] = []
    for check in policy.checks:
        all_findings.extend(check(path))

    return WorkspaceReadinessReport(
        workspace_path=path,
        policy_id=policy.policy_id,
        findings=all_findings,
    )
