"""GitLab implementation of the ScmAdapter Protocol (RAISE-16773).

Shells out to ``glab``. Two deliberate departures from what the S3 design
document sketched, both found by checking the installed CLI rather than
trusting the doc (design §7 asked for exactly this):

``--yes`` on create and merge
    ``glab`` prompts for confirmation even with ``--no-editor``. These calls run
    under ``capture_output``, i.e. without a TTY, so the prompt would not be
    seen — the command would simply hang until the timeout.

``glab api`` for CI status instead of ``glab mr view --output json``
    glab 1.36.0's ``mr view`` has no JSON flag at all. The REST endpoint
    (``head_pipeline.status``) is a GitLab API contract rather than a CLI
    presentation detail, so it is also the more stable of the two reads.

Open item handed to S4 (RAISE-16774): ``glab mr merge`` defaults ``--auto-merge``
to true, which can *schedule* a merge behind a running pipeline rather than
performing one. S4 gates on ``get_mr_ci_status`` before calling ``merge_mr``, so
the distinction only matters if that gate is ever relaxed — verify against a
live MR there before relying on merge_mr being immediate.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any
from urllib.parse import quote

from raise_cli.scm.adapter import CiStatus, ScmCommandError

_TIMEOUT_S = 120.0

_MR_URL_RE = re.compile(
    r"^https?://[^/\s]+/(?P<path>.+?)/-/merge_requests/(?P<iid>\d+)/?$"
)
_MR_URL_IN_OUTPUT_RE = re.compile(r"https?://\S+/-/merge_requests/\d+")

_AUTH_MARKERS = ("401", "unauthorized", "authentication", "not logged in")
_AUTH_HINT = "session may have expired — run: glab auth login --hostname <host>"

# D-S3-6. Anything absent from these two sets is 'failed' on purpose: a status
# we do not recognise has not told us the pipeline passed.
_PENDING_STATUSES = frozenset(
    {"created", "waiting_for_resource", "preparing", "pending", "scheduled"}
)
_RUNNING_STATUSES = frozenset({"running"})


class GitLabAdapter:
    """Merge requests on GitLab, via the ``glab`` CLI."""

    def create_mr(
        self,
        *,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
    ) -> str:
        """Open a merge request and return its URL.

        Raises:
            ScmCommandError: ``glab`` is missing, failed, timed out, or printed
                no merge-request URL we could parse.
        """
        result = self._run(
            "mr",
            "create",
            "--source-branch",
            source_branch,
            "--target-branch",
            target_branch,
            "--title",
            title,
            "--description",
            description,
            "--no-editor",
            "--yes",
        )
        self._check(result, action="create a merge request")

        match = _MR_URL_IN_OUTPUT_RE.search(result.stdout)
        if match is None:
            raise ScmCommandError(
                "glab reported success but printed no merge request URL — "
                "refusing to report an MR that cannot be linked. Output was:\n"
                f"{result.stdout.strip()}"
            )
        return match.group(0)

    def merge_mr(self, *, mr_url: str, delete_source_branch: bool = True) -> None:
        """Merge an open merge request.

        Raises:
            ScmCommandError: the URL is not a merge request URL, or glab failed.
        """
        project_path, iid = _parse_mr_url(mr_url)
        args = ["mr", "merge", iid, "--repo", project_path, "--yes"]
        if delete_source_branch:
            args.append("--remove-source-branch")

        result = self._run(*args)
        self._check(result, action=f"merge {mr_url}")

    def get_mr_ci_status(self, *, mr_url: str) -> CiStatus:
        """Read the merge request's current CI verdict. One shot, no polling.

        Fail-closed per D-S3-6: only ``success`` is a green light, and an MR with
        no pipeline at all maps to ``failed`` rather than to a benign value.

        A failure to *read* the status raises instead of returning ``failed``.
        Collapsing the two would make an expired token look identical to a red
        pipeline, and the caller would report the wrong reason for blocking.

        Raises:
            ScmCommandError: the URL is unparseable, the API call failed, or the
                response was not JSON.
        """
        project_path, iid = _parse_mr_url(mr_url)
        endpoint = f"projects/{quote(project_path, safe='')}/merge_requests/{iid}"

        result = self._run("api", endpoint)
        self._check(result, action=f"read CI status for {mr_url}")

        try:
            payload: Any = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ScmCommandError(
                f"glab api {endpoint} returned output that is not JSON: "
                f"{result.stdout.strip()[:200]}"
            ) from exc

        if not isinstance(payload, dict):
            raise ScmCommandError(
                f"glab api {endpoint} returned {type(payload).__name__}, expected object"
            )

        pipeline = payload.get("head_pipeline")
        if not isinstance(pipeline, dict):
            return "failed"
        status = pipeline.get("status")
        if not isinstance(status, str):
            return "failed"

        return _map_pipeline_status(status)

    # -- subprocess plumbing -------------------------------------------------

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ["glab", *args],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_S,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ScmCommandError(
                "glab is not installed or not on PATH — install the GitLab CLI "
                "(https://gitlab.com/gitlab-org/cli) to create merge requests."
            ) from exc
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ScmCommandError(f"glab {' '.join(args)} failed: {exc}") from exc

    @staticmethod
    def _check(result: subprocess.CompletedProcess[str], *, action: str) -> None:
        if result.returncode == 0:
            return
        stderr = result.stderr.strip()
        message = f"glab failed to {action} (exit {result.returncode}): {stderr}"
        if any(marker in stderr.lower() for marker in _AUTH_MARKERS):
            message = f"{message}\n{_AUTH_HINT}"
        raise ScmCommandError(message)


def _parse_mr_url(mr_url: str) -> tuple[str, str]:
    """Split a merge request URL into ``(project_path, iid)``.

    Raises:
        ScmCommandError: the URL is not a GitLab merge request URL. Guessing an
            IID from a malformed URL risks acting on the wrong merge request.
    """
    match = _MR_URL_RE.match(mr_url.strip())
    if match is None:
        raise ScmCommandError(
            f"Not a GitLab merge request URL: {mr_url!r} — expected the form "
            "https://<host>/<group>/<project>/-/merge_requests/<iid>"
        )
    return match.group("path"), match.group("iid")


def _map_pipeline_status(status: str) -> CiStatus:
    """Normalise a GitLab pipeline status onto :data:`CiStatus` (D-S3-6)."""
    normalised = status.strip().lower()
    if normalised in _RUNNING_STATUSES:
        return "running"
    if normalised in _PENDING_STATUSES:
        return "pending"
    if normalised == "success":
        return "success"
    return "failed"
