"""Workspace contracts — generic readiness, health, and provisioning abstractions.

These models are workspace-generic: they do not encode git or worktree assumptions.
Workspace-specific policies (e.g. git worktree) live near their provisioning code.

Public API:
    WorkspaceReadinessFinding
    WorkspaceReadinessPolicy
    WorkspaceReadinessReport
    evaluate_workspace_readiness
"""

from raise_cli.workspace.readiness import (
    WorkspaceReadinessFinding,
    WorkspaceReadinessPolicy,
    WorkspaceReadinessReport,
    evaluate_workspace_readiness,
)

__all__ = [
    "WorkspaceReadinessFinding",
    "WorkspaceReadinessPolicy",
    "WorkspaceReadinessReport",
    "evaluate_workspace_readiness",
]
