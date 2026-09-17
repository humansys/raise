"""Claude Code adapter — subprocess dispatch to the ``claude`` CLI (RAISE-17423).

Invokes ``claude -p --output-format json`` and parses the structured
response into a ``ReviewResult``. The prompt is delivered via stdin rather
than argv (RAISE-17484): Linux's ``MAX_ARG_STRLEN`` (128 KiB) rejects any
single exec argument beyond that, and large diffs routinely exceed it.
Fail-closed: timeout, non-zero exit, OS-level dispatch failures (including
``OSError`` such as E2BIG), malformed output, and missing fields all
resolve to ``fail``.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from typing import Any

from raise_cli.harness_review.adapter import (
    ReviewContext,
    ReviewFinding,
    ReviewResult,
    ReviewVerdict,
)

DEFAULT_TIMEOUT_SECONDS = 300.0

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n(.*)\n```\s*$", re.DOTALL)


def _strip_markdown_fences(text: str) -> str:
    """Remove a single markdown code fence if it wraps the entire text."""
    m = _FENCE_RE.match(text)
    return m.group(1) if m else text


class ClaudeCodeAdapter:
    """Review adapter that dispatches to a local ``claude`` CLI binary."""

    def __init__(self, *, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._timeout = timeout_seconds

    def request_review(
        self,
        *,
        diff: str,
        context: ReviewContext,
        dimensions: tuple[str, ...],
    ) -> ReviewResult:
        """Request a review of the given diff and return a structured verdict."""
        prompt = self._build_prompt(diff, context, dimensions)
        start = time.monotonic()
        try:
            proc = subprocess.run(
                ["claude", "-p", "--output-format", "json"],
                input=prompt,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._timeout,
                check=False,
            )
        except FileNotFoundError:
            return self._fail_result("claude binary not found in PATH", start)
        except subprocess.TimeoutExpired:
            return self._fail_result(f"timeout after {self._timeout}s", start)
        except OSError as exc:
            return self._fail_result(f"subprocess dispatch failed: {exc}", start)

        if proc.returncode != 0:
            stderr = proc.stderr.strip() if proc.stderr else "unknown error"
            return self._fail_result(
                f"claude exited with code {proc.returncode}: {stderr}", start
            )

        return self._parse_response(proc.stdout, start)

    def _build_prompt(
        self,
        diff: str,
        context: ReviewContext,
        dimensions: tuple[str, ...],
    ) -> str:
        dims_str = ", ".join(dimensions)
        return (
            f"Review this diff for: {dims_str}.\n\n"
            f"Design context: {context.design_excerpt}\n"
            f"Scope: {context.scope_summary}\n\n"
            f"Diff:\n{diff}\n\n"
            "Respond with JSON: "
            '{"verdict": "pass"|"fail", "findings": ['
            '{"file": str, "line": int, "summary": str, '
            '"fix_suggestion": str, "dimension": str}]}'
        )

    def _parse_response(self, stdout: str, start: float) -> ReviewResult:
        text = _strip_markdown_fences(stdout.strip())
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return self._fail_result("malformed JSON response", start)

        if not isinstance(data, dict):
            return self._fail_result("response is not a JSON object", start)

        envelope_type = data.get("type")
        if (envelope_type is not None and envelope_type != "result") or (
            data.get("is_error") is True
        ):
            return self._fail_result(self._describe_error_envelope(data), start)

        data = self._unwrap_envelope(data)

        verdict_raw = data.get("verdict")
        if verdict_raw not in ("pass", "fail"):
            return self._fail_result(
                f"missing or invalid verdict field: {verdict_raw!r}", start
            )

        verdict: ReviewVerdict = verdict_raw
        findings = self._parse_findings(data.get("findings", []))
        elapsed = time.monotonic() - start

        return ReviewResult(
            verdict=verdict,
            findings=findings,
            harness="claude",
            duration_seconds=elapsed,
        )

    @staticmethod
    def _describe_error_envelope(data: dict[str, Any]) -> str:
        """Extract a human-readable reason from a failed invocation envelope.

        Claude Code reports invocation-level failures two ways: a top-level
        ``{"type": "error", "error": {...}}`` envelope (rare — dispatch
        failed before any turn ran), or, more commonly, a completed turn
        that still fails mid-execution (auth, rate limit): ``{"type":
        "result", "subtype": "error_during_execution", "is_error": true,
        "result": "<human-readable error text>"}``. Both shapes must surface
        their real message instead of letting the missing ``verdict`` field
        downstream produce a generic failure indistinguishable from a
        malformed response.
        """
        envelope_type = data.get("type")
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message:
                return f"claude returned type={envelope_type!r}: {message}"
        if isinstance(error, str) and error:
            return f"claude returned type={envelope_type!r}: {error}"
        result_text = data.get("result")
        if isinstance(result_text, str) and result_text:
            subtype = data.get("subtype")
            return f"claude reported an error (subtype={subtype!r}): {result_text}"
        return f"claude returned unexpected envelope type={envelope_type!r}: {data!r}"

    @staticmethod
    def _unwrap_envelope(data: dict[str, Any]) -> dict[str, Any]:
        """Unwrap Claude Code's ``--output-format json`` envelope.

        The envelope has ``{"type": "result", "result": "<json-string>", ...}``.
        The inner result may be raw JSON or markdown-fenced JSON (common when
        the prompt is complex). Both forms are handled.
        """
        if data.get("type") == "result" and isinstance(data.get("result"), str):
            text = data["result"].strip()
            text = _strip_markdown_fences(text)
            try:
                inner = json.loads(text)
                if isinstance(inner, dict):
                    return inner
            except (json.JSONDecodeError, ValueError):
                pass
        return data

    def _parse_findings(
        self,
        raw_findings: Any,
    ) -> tuple[ReviewFinding, ...]:
        if not isinstance(raw_findings, list):
            return ()
        findings: list[ReviewFinding] = []
        for item in raw_findings:
            if not isinstance(item, dict):
                continue
            try:
                findings.append(
                    ReviewFinding(
                        file=str(item.get("file", "")),
                        line=int(item.get("line", 0)),
                        summary=str(item.get("summary", "")),
                        fix_suggestion=str(item.get("fix_suggestion", "")),
                        dimension=str(item.get("dimension", "")),
                    )
                )
            except (TypeError, ValueError):
                continue
        return tuple(findings)

    def _fail_result(self, reason: str, start: float) -> ReviewResult:
        elapsed = time.monotonic() - start
        return ReviewResult(
            verdict="fail",
            findings=(
                ReviewFinding(
                    file="",
                    line=0,
                    summary=reason,
                    fix_suggestion="",
                    dimension="infrastructure",
                ),
            ),
            harness="claude",
            duration_seconds=elapsed,
        )
