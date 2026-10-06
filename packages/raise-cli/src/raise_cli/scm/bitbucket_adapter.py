"""Bitbucket SCM adapter — unimplemented stub (RAISE-16771).

``branches.scm: bitbucket`` is accepted by the manifest as of RAISE-16771, so
this class exists to make that selection fail with a sentence a developer can
act on instead of an ImportError or an AttributeError.

Method signatures follow ADR-2026-08-29 (SCM Adapter Protocol) exactly, so
that when S3 (RAISE-16773) introduces the Protocol this class conforms
structurally with no edit here. The real implementation is RAISE-16775.
"""

from __future__ import annotations

from typing import Literal

PROVIDER = "Bitbucket"
IMPLEMENTATION_STORY = "RAISE-16775"

_MESSAGE = f"{PROVIDER} adapter not implemented — see {IMPLEMENTATION_STORY}"


class BitbucketAdapter:
    """Placeholder adapter for Bitbucket repositories.

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
        """Open a pull request in Bitbucket Cloud and return its URL.

        This method corresponds to ``ScmAdapter.create_mr`` in the Protocol
        defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: Bitbucket Cloud does not ship an official CLI analogous
            to ``glab`` or ``gh``. Use the Bitbucket Cloud REST API directly
            (requires an app password or OAuth 2.0 token).

            API: POST
            ``https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests``
            with a JSON body::

                {
                    "title": "<title>",
                    "description": "<description>",
                    "source": {"branch": {"name": "<source_branch>"}},
                    "destination": {"branch": {"name": "<target_branch>"}},
                    "close_source_branch": false
                }

            The response ``links.html.href`` field contains the PR web URL
            that this method must return.

            Tracking ticket: RAISE-16775.

        Args:
            title: The pull-request title shown in the Bitbucket UI.
            description: Body text / markdown for the pull-request description.
            source_branch: Local branch name to merge from (e.g. ``story/s16775/...``).
            target_branch: Target branch name (e.g. ``release/3.1.0``).

        Returns:
            URL of the created pull request.

        Raises:
            NotImplementedError: Always — Bitbucket support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)

    def merge_mr(self, *, mr_url: str, delete_source_branch: bool = True) -> None:
        """Merge a Bitbucket Cloud pull request.

        This method corresponds to ``ScmAdapter.merge_mr`` in the Protocol
        defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: No official Bitbucket CLI; use the REST API.

            API: POST
            ``https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{id}/merge``
            with a JSON body::

                {
                    "type": "pullrequest",
                    "close_source_branch": <bool>
                }

            The PR id must be extracted from *mr_url*; it is the integer at the
            end of the path, e.g. ``/pull-requests/42`` → ``42``.

            Tracking ticket: RAISE-16775.

        Args:
            mr_url: The full URL of the pull request as returned by ``create_mr``.
            delete_source_branch: When ``True`` (default), the source branch is
                deleted after the PR is merged (``close_source_branch`` in the
                Bitbucket API).

        Raises:
            NotImplementedError: Always — Bitbucket support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)

    def get_mr_ci_status(
        self, *, mr_url: str
    ) -> Literal["pending", "running", "success", "failed"]:
        """Report the Bitbucket Pipelines build status for a pull request.

        This method corresponds to ``ScmAdapter.get_mr_ci_status`` in the
        Protocol defined by S3 (RAISE-16773).

        Implementation guide:
            CLI tool: No official Bitbucket CLI; use the REST API.

            API: GET
            ``https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{id}/statuses``
            — each status object's ``state`` field maps to the Protocol return
            values as follows:
            ``"INPROGRESS"`` → ``"running"``, ``"SUCCESSFUL"`` → ``"success"``,
            ``"FAILED"`` → ``"failed"``; absence of any status → ``"pending"``.

            Tracking ticket: RAISE-16775.

        Args:
            mr_url: The full URL of the pull request as returned by ``create_mr``.

        Returns:
            One of ``"pending"``, ``"running"``, ``"success"``, or ``"failed"``.

        Raises:
            NotImplementedError: Always — Bitbucket support is not yet implemented.
        """
        raise NotImplementedError(_MESSAGE)
