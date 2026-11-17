"""Azure DevOps SCM adapter — unimplemented stub (RAISE-16771).

``branches.scm: azuredevops`` is accepted by the manifest as of RAISE-16771,
so this class exists to make that selection fail with a sentence a developer
can act on instead of an ImportError or an AttributeError.

Method signatures follow ADR-2026-08-29 (SCM Adapter Protocol) exactly, so
that when S3 (RAISE-16773) introduces the Protocol this class conforms
structurally with no edit here. The real implementation is RAISE-16775.
"""

from __future__ import annotations

from typing import Literal

PROVIDER = "AzureDevOps"
IMPLEMENTATION_STORY = "RAISE-16775"

_MESSAGE = f"{PROVIDER} adapter not implemented — see {IMPLEMENTATION_STORY}"


class AzureDevOpsAdapter:
    """Placeholder adapter for Azure DevOps repositories.

    Instantiation succeeds on purpose: selecting the provider is a valid
    configuration, and raising in ``__init__`` would move the failure from the
    unsupported operation to the wiring that merely resolved it.
    """

    def create_mr(
        self,
        *,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
    ) -> str:
        """Open a pull request in Azure DevOps and return its URL.

        This method corresponds to ``ScmAdapter.create_mr`` in the Protocol
        defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: ``az devops`` (Azure CLI extension, requires
            ``az extension add --name azure-devops`` and
            ``az devops configure --defaults organization=<org> project=<proj>``).

            API alternative: POST
            ``https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests?api-version=7.1``
            with a JSON body containing ``sourceRefName``, ``targetRefName``,
            ``title``, and ``description``.

            Expected return value: the pull-request web URL, e.g.
            ``https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{id}``.

            Tracking ticket: RAISE-16775.

        Args:
            title: The pull-request title shown in the Azure DevOps UI.
            description: Body text / markdown for the pull-request description.
            source_branch: Local branch name to merge from (e.g. ``story/s16775/...``).
            target_branch: Target branch name (e.g. ``release/3.1.0``).

        Returns:
            URL of the created pull request.

        Raises:
            NotImplementedError: Always — Azure DevOps support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)

    def merge_mr(self, *, mr_url: str, delete_source_branch: bool = True) -> None:
        """Complete (merge) an Azure DevOps pull request.

        This method corresponds to ``ScmAdapter.merge_mr`` in the Protocol
        defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: ``az repos pr update --id <id> --status completed``
            (the PR id must be parsed from *mr_url*).

            API alternative: PATCH
            ``https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests/{pullRequestId}?api-version=7.1``
            with ``{"status": "completed", "completionOptions": {"deleteSourceBranch": <bool>}}``.

            To extract the PR id from *mr_url*: the integer at the end of the
            path segment ``/pullrequest/{id}``.

            Tracking ticket: RAISE-16775.

        Args:
            mr_url: The full URL of the pull request as returned by ``create_mr``.
            delete_source_branch: When ``True`` (default), the source branch is
                deleted after the PR is completed.

        Raises:
            NotImplementedError: Always — Azure DevOps support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)

    def get_mr_ci_status(
        self, *, mr_url: str
    ) -> Literal["pending", "running", "success", "failed"]:
        """Report the Azure Pipelines build status for a pull request.

        This method corresponds to ``ScmAdapter.get_mr_ci_status`` in the
        Protocol defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: ``az repos pr show --id <id> --query "completionOptions"``
            does not expose pipeline status directly; use the Statuses API
            instead.

            API: GET
            ``https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests/{pullRequestId}/statuses?api-version=7.1``
            — the most recent status object's ``state`` field maps to the
            Protocol return values as follows:
            ``"pending"`` → ``"pending"``, ``"running"`` → ``"running"``,
            ``"succeeded"`` → ``"success"``, ``"failed"`` / ``"error"`` → ``"failed"``.

            Tracking ticket: RAISE-16775.

        Args:
            mr_url: The full URL of the pull request as returned by ``create_mr``.

        Returns:
            One of ``"pending"``, ``"running"``, ``"success"``, or ``"failed"``.

        Raises:
            NotImplementedError: Always — Azure DevOps support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)
