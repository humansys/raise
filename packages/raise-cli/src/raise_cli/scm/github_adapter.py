"""GitHub implementation of the ScmAdapter Protocol (RAISE-16773).

Shells out to ``gh``. PAT-129 lives here and in the GitLab adapter: GitHub says
``pr``, GitLab says ``mr``, and these two modules are the only code allowed to
know the difference. Everything upstream speaks the Protocol's GitLab-flavoured
vocabulary.

``gh pr merge`` is invoked with an explicit ``--merge``. Without a method flag
``gh`` opens an interactive picker, and these calls run under
``capture_output`` — there is no TTY to pick from. Same reasoning as the
GitLab adapter's ``--yes``.

Status is harder than GitLab's. GitLab reports one pipeline status; GitHub
reports a rollup of many checks in two shapes (``CheckRun`` carrying
status/conclusion, ``StatusContext`` carrying state). The combination is not
"last one wins" — see :func:`_combine`.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from raise_cli.scm.adapter import CiStatus, ScmCommandError

_TIMEOUT_S = 120.0

_PR_URL_IN_OUTPUT_RE = re.compile(r"https?://\S+/pull/\d+")

_AUTH_MARKERS = ("401", "unauthorized", "authentication", "not logged in", "auth")
_AUTH_HINT = "run: gh auth login"

# D-S3-6. SKIPPED is green here and red on GitLab, and the asymmetry is
# intentional: GitLab's skipped is pipeline-level (nothing was validated),
# GitHub's is per-check and is the normal result of a path filter.
_SUCCESS_CONCLUSIONS = frozenset({"SUCCESS", "SKIPPED"})
_PENDING_CHECK_STATUSES = frozenset({"QUEUED", "PENDING", "WAITING", "REQUESTED"})
_RUNNING_CHECK_STATUSES = frozenset({"IN_PROGRESS"})

_CONTEXT_STATES: dict[str, CiStatus] = {
    "SUCCESS": "success",
    "PENDING": "pending",
    "EXPECTED": "pending",
    "FAILURE": "failed",
    "ERROR": "failed",
}

# Worst-first. Waiting longer cannot turn an already-red rollup green, so a
# failure short-circuits the whole verdict.
_PRECEDENCE: tuple[CiStatus, ...] = ("failed", "running", "pending", "success")


class GitHubAdapter:
    """Pull requests on GitHub, via the ``gh`` CLI."""

    def create_mr(
        self,
        *,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
    ) -> str:
        """Open a pull request and return its URL.

        Raises:
            ScmCommandError: ``gh`` is missing, failed, timed out, or printed no
                pull request URL we could parse.
        """
        result = self._run(
            "pr",
            "create",
            "--head",
            source_branch,
            "--base",
            target_branch,
            "--title",
            title,
            "--body",
            description,
        )
        self._check(result, action="create a pull request")

        match = _PR_URL_IN_OUTPUT_RE.search(result.stdout)
        if match is None:
            raise ScmCommandError(
                "gh reported success but printed no pull request URL — refusing "
                "to report a PR that cannot be linked. Output was:\n"
                f"{result.stdout.strip()}"
            )
        return match.group(0)

    def merge_mr(self, *, mr_url: str, delete_source_branch: bool = True) -> None:
        """Merge an open pull request.

        Raises:
            ScmCommandError: ``gh`` failed.
        """
        args = ["pr", "merge", mr_url, "--merge"]
        if delete_source_branch:
            args.append("--delete-branch")

        result = self._run(*args)
        self._check(result, action=f"merge {mr_url}")

    def get_mr_ci_status(self, *, mr_url: str) -> CiStatus:
        """Read the pull request's rolled-up CI verdict. One shot, no polling.

        Fail-closed per D-S3-6: a PR with no checks at all is ``failed``, and any
        check whose shape we cannot read counts as ``failed`` rather than being
        ignored.

        A failure to *read* the rollup raises instead of returning ``failed``, so
        a revoked token stays distinguishable from a red check.

        Raises:
            ScmCommandError: the ``gh`` call failed or returned non-JSON.
        """
        result = self._run("pr", "view", mr_url, "--json", "statusCheckRollup")
        self._check(result, action=f"read CI status for {mr_url}")

        try:
            payload: Any = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ScmCommandError(
                "gh pr view returned output that is not JSON: "
                f"{result.stdout.strip()[:200]}"
            ) from exc

        if not isinstance(payload, dict):
            raise ScmCommandError(
                f"gh pr view returned {type(payload).__name__}, expected an object"
            )

        checks = payload.get("statusCheckRollup")
        if not isinstance(checks, list) or not checks:
            return "failed"

        return _combine([_map_check(check) for check in checks])

    # -- subprocess plumbing -------------------------------------------------

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ["gh", *args],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_S,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ScmCommandError(
                "gh is not installed or not on PATH — install the GitHub CLI "
                "(https://cli.github.com) to create pull requests."
            ) from exc
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ScmCommandError(f"gh {' '.join(args)} failed: {exc}") from exc

    @staticmethod
    def _check(result: subprocess.CompletedProcess[str], *, action: str) -> None:
        if result.returncode == 0:
            return
        stderr = result.stderr.strip()
        message = f"gh failed to {action} (exit {result.returncode}): {stderr}"
        if any(marker in stderr.lower() for marker in _AUTH_MARKERS):
            message = f"{message}\n{_AUTH_HINT}"
        raise ScmCommandError(message)


def _map_check(check: object) -> CiStatus:
    """Map one rollup node to :data:`CiStatus`, failing closed on anything odd."""
    if not isinstance(check, dict):
        return "failed"

    conclusion = check.get("conclusion")
    if isinstance(conclusion, str) and conclusion:
        return "success" if conclusion.upper() in _SUCCESS_CONCLUSIONS else "failed"

    status = check.get("status")
    if isinstance(status, str) and status:
        upper = status.upper()
        if upper in _RUNNING_CHECK_STATUSES:
            return "running"
        if upper in _PENDING_CHECK_STATUSES:
            return "pending"
        # COMPLETED with no conclusion, or a status GitHub added since: we were
        # not told it passed.
        return "failed"

    state = check.get("state")
    if isinstance(state, str):
        return _CONTEXT_STATES.get(state.upper(), "failed")

    return "failed"


def _combine(statuses: list[CiStatus]) -> CiStatus:
    """Reduce per-check verdicts to one, worst-first.

    ``failed`` dominates ``running`` and ``pending`` so a doomed PR is reported
    immediately rather than after the poll timeout.
    """
    for candidate in _PRECEDENCE:
        if candidate in statuses:
            return candidate
    return "failed"
