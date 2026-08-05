"""Conformance checker for post-session governance analysis.

Compares agent behavior in a completed session against the framework
governance contract. Detects three violation types:

- WORKAROUND: agent circumvented a problem instead of fixing it
  (type: ignore, --no-verify, broad except, silent conflict resolve)
- JIDOKA: agent didn't stop on a defect — continued after gate/test failure
- GOVERNANCE_SKIP: mandatory governance step was omitted

Also detects tool reliability violations (E15436 root-cause patterns):
- bash-interface-guess: used a symbol/module that doesn't exist (RC1)
- bash-retry-identical: retried the same failing command unchanged (RC2)
- bash-command-not-found: invoked a CLI tool that isn't installed (RC2/RC3)

Unlike the insight classifier (turn-level content analysis), this module
analyzes action SEQUENCES — what the agent did vs what it should have done.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel

from raise_cli.distillation.parser import TurnRecord, TurnType

# ── Data model ────────────────────────────────────────────────────────


class ViolationType(str, Enum):
    """Category of governance violation detected in a session."""

    WORKAROUND = "workaround"
    JIDOKA = "jidoka"
    GOVERNANCE_SKIP = "skip"


class Violation(BaseModel):
    """Single governance violation with evidence and location."""

    type: ViolationType
    turn_index: int
    severity: str
    rule: str
    description: str
    evidence: str


class ConformanceReport(BaseModel):
    """Result of running all conformance detectors on a session."""

    total_turns: int
    violations: list[Violation]


# ── Workaround patterns ──────────────────────────────────────────────

_WORKAROUND_CODE_PATTERNS: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        re.compile(r"#\s*type:\s*ignore"),
        "type-suppress",
        "high",
        "Type checker suppressed instead of fixing the type error",
    ),
    (
        re.compile(r"#\s*noqa"),
        "lint-suppress",
        "medium",
        "Linter warning suppressed instead of fixing the issue",
    ),
    (
        re.compile(r"except\s+(Exception|BaseException)\s*:"),
        "broad-except",
        "medium",
        "Overly broad exception catch — masks real errors",
    ),
]

_WORKAROUND_BASH_PATTERNS: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        re.compile(r"--no-verify"),
        "hook-bypass",
        "high",
        "Git hooks bypassed instead of fixing the hook failure",
    ),
    (
        re.compile(r"(push|reset)\s+--force\b"),
        "force-op",
        "high",
        "Forced a destructive git operation",
    ),
    (
        re.compile(r"checkout\s+--(theirs|ours)\b"),
        "silent-conflict-resolve",
        "high",
        "Merge conflict resolved silently without discussion",
    ),
]


def _extract_bash_commands(record: TurnRecord) -> list[str]:
    """Extract Bash command strings from a turn's tool_inputs."""
    commands: list[str] = []
    for tool_data in record.tool_inputs.values():
        if not isinstance(tool_data, dict):
            continue
        if tool_data.get("name") != "Bash":
            continue
        inp: Any = tool_data.get("input", {})
        if isinstance(inp, dict):
            cmd = inp.get("command", "")
            if isinstance(cmd, str) and cmd:
                commands.append(cmd)
    return commands


def _net_new_content(new_string: str, old_string: str) -> str:
    """Return lines in *new_string* that are absent from *old_string* (RAISE-15458)."""
    old_lines = set(old_string.splitlines())
    return "\n".join(ln for ln in new_string.splitlines() if ln not in old_lines)


def _collect_last_edits(
    records: list[TurnRecord],
) -> dict[str, tuple[int, str]]:
    """Collect the net-new edit content per file path across all assistant turns.

    For Edit tool calls, only the lines in ``new_string`` that are NOT in
    ``old_string`` are returned — pre-existing patterns (e.g. ``# noqa``)
    that were already in the file before the edit are excluded
    (RAISE-15458).  For Write tool calls, the full content is returned
    since there is no baseline to diff against.
    """
    last_edit_per_file: dict[str, tuple[int, str]] = {}
    for rec in records:
        if rec.turn_type != TurnType.ASSISTANT:
            continue
        for tool_data in rec.tool_inputs.values():
            if not isinstance(tool_data, dict):
                continue
            if tool_data.get("name") not in ("Edit", "Write"):
                continue
            inp: Any = tool_data.get("input", {})
            if not isinstance(inp, dict):
                continue
            file_path: str = inp.get("file_path", inp.get("path", ""))
            fkey = file_path or f"_unknown_{rec.index}"

            new_string = inp.get("new_string", "")
            old_string = inp.get("old_string", "")
            content = inp.get("content", "")

            if isinstance(new_string, str) and new_string:
                net_new = (
                    _net_new_content(new_string, old_string)
                    if isinstance(old_string, str) and old_string
                    else new_string
                )
                if net_new:
                    last_edit_per_file[fkey] = (rec.index, net_new)
            elif isinstance(content, str) and content:
                last_edit_per_file[fkey] = (rec.index, content)
    return last_edit_per_file


def detect_workarounds(records: list[TurnRecord]) -> list[Violation]:
    """Scan assistant turns for workaround patterns."""
    violations: list[Violation] = []

    for rec in records:
        if rec.turn_type != TurnType.ASSISTANT:
            continue
        for cmd in _extract_bash_commands(rec):
            for pattern, rule, severity, desc in _WORKAROUND_BASH_PATTERNS:
                if pattern.search(cmd):
                    violations.append(
                        Violation(
                            type=ViolationType.WORKAROUND,
                            turn_index=rec.index,
                            severity=severity,
                            rule=rule,
                            description=desc,
                            evidence=cmd[:200],
                        )
                    )

    # RAISE-15458: only check the final edit of each file, not intermediate debug edits.
    for turn_index, edit_text in _collect_last_edits(records).values():
        for pattern, rule, severity, desc in _WORKAROUND_CODE_PATTERNS:
            if pattern.search(edit_text):
                violations.append(
                    Violation(
                        type=ViolationType.WORKAROUND,
                        turn_index=turn_index,
                        severity=severity,
                        rule=rule,
                        description=desc,
                        evidence=edit_text[:200],
                    )
                )

    return violations


# ── Jidoka violations ─────────────────────────────────────────────────

_GATE_CHECK_RE = re.compile(r"rai gate check\b")
_PYTEST_RE = re.compile(r"(uv run )?pytest\b|uv run python -m pytest")
_FAIL_RE = re.compile(r"\bFAIL|FAILED|Error:|error:", re.IGNORECASE)
_COMMIT_RE = re.compile(r"git (commit|push)\b")
_FIX_TOOLS = frozenset({"Edit", "Write"})


def detect_jidoka_violations(records: list[TurnRecord]) -> list[Violation]:
    """Detect gate/test failure followed by commit instead of fix."""
    violations: list[Violation] = []
    pending_failure: tuple[int, str] | None = None
    last_check_type: str | None = None
    # RAISE-15459: track whether the last assistant turn already applied a fix
    # so pre-commit hook failures in that same turn don't create spurious pending_failure.
    last_assistant_had_fix: bool = False

    for rec in records:
        if rec.turn_type == TurnType.ASSISTANT:
            had_fix = bool(_FIX_TOOLS & set(rec.tool_names))
            commands = _extract_bash_commands(rec)
            is_gate = any(_GATE_CHECK_RE.search(c) for c in commands)
            is_test = any(_PYTEST_RE.search(c) for c in commands)
            if is_gate or is_test:
                last_check_type = "gate-fail" if is_gate else "test-fail"
                pending_failure = None
                last_assistant_had_fix = had_fix
                continue

            if pending_failure is not None:
                if had_fix:
                    pending_failure = None
                    last_assistant_had_fix = had_fix
                    continue

                is_commit = any(_COMMIT_RE.search(c) for c in commands)
                if is_commit:
                    fail_idx, fail_type = pending_failure
                    violations.append(
                        Violation(
                            type=ViolationType.JIDOKA,
                            turn_index=rec.index,
                            severity="high",
                            rule=f"{fail_type}-continue",
                            description=(
                                f"Agent committed/pushed after {fail_type} failure "
                                f"at turn {fail_idx} without fixing"
                            ),
                            evidence=" | ".join(commands)[:200],
                        )
                    )
                    pending_failure = None

            last_assistant_had_fix = had_fix

        elif rec.turn_type == TurnType.TOOL_RESULT and _FAIL_RE.search(
            rec.content_text
        ):
            # Only open a pending failure if the turn that triggered this result
            # did not already have a fix tool call (RAISE-15459).
            # RAISE-15536/15537: only open pending_failure when an explicit
            # pytest/rai-gate check ran (last_check_type is set). Ignore
            # _FAIL_RE matches in git/pre-commit output.
            if (
                pending_failure is None
                and not last_assistant_had_fix
                and last_check_type is not None
            ):
                pending_failure = (rec.index, last_check_type)

    return violations


# ── Tool reliability violations (E15436 RC1/RC2/RC3) ─────────────────

_IMPORT_ERROR_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|cannot import name"
    r"|AttributeError:.*has no attribute)",
    re.IGNORECASE,
)
_COMMAND_NOT_FOUND_RE = re.compile(
    r"(command not found|No such file or directory: '.*'"
    r"|zsh: command not found|bash: \S+: command not found)",
    re.IGNORECASE,
)
_BASH_NONZERO_RE = re.compile(r"Exit code [1-9]\d*", re.IGNORECASE)
_TRIVIAL_LINE_RE = re.compile(r"^\s*(cd\s+\S+|export\s+\S+=.*)\s*$")


def _normalize_cmd_key(cmd: str) -> str:
    """Return a 80-char key for retry-identical detection, ignoring leading cd/export lines.

    RAISE-15462: when the agent prefixes commands with `cd /long/path`, the
    path alone can exceed 80 chars, making unrelated commands appear identical.
    Strip trivial prefix lines (cd, export) before slicing.
    """
    lines = [line for line in cmd.split("\n") if line.strip()]
    non_trivial = [line for line in lines if not _TRIVIAL_LINE_RE.match(line)]
    effective = non_trivial if non_trivial else lines
    return " ".join(effective).strip()[:80]


def detect_tool_reliability_violations(records: list[TurnRecord]) -> list[Violation]:  # noqa: C901
    """Detect E15436 root-cause patterns: interface-guess, blind-retry, command-not-found."""
    violations: list[Violation] = []
    last_bash_cmds: list[str] = []
    had_failure: bool = False

    for rec in records:
        if rec.turn_type == TurnType.ASSISTANT:
            commands = _extract_bash_commands(rec)

            # RAISE-15460: check fix tools BEFORE retry detection so that
            # Edit+Bash(commit) in the same turn is not flagged as retry-identical.
            current_has_fix = bool(_FIX_TOOLS & set(rec.tool_names))
            if current_has_fix:
                had_failure = False

            if had_failure and commands:
                # bash-retry-identical: same normalized key retried after failure.
                # RAISE-15462: normalize strips leading cd/export lines so a long
                # cd-prefix doesn't make unrelated commands appear identical.
                for cmd in commands:
                    key = _normalize_cmd_key(cmd)
                    if any(
                        key == _normalize_cmd_key(prev)
                        for prev in last_bash_cmds
                        if prev.strip()
                    ):
                        violations.append(
                            Violation(
                                type=ViolationType.WORKAROUND,
                                turn_index=rec.index,
                                severity="medium",
                                rule="bash-retry-identical",
                                description="Agent retried the exact same failing command without changing the approach",
                                evidence=cmd[:200],
                            )
                        )
                        break  # one violation per turn is enough

            if commands:
                last_bash_cmds = commands

        elif rec.turn_type == TurnType.TOOL_RESULT:
            text = rec.content_text

            # bash-interface-guess (RC1): import/attribute errors mean the agent
            # called code that doesn't exist — should have queried the graph first
            if _IMPORT_ERROR_RE.search(text) and last_bash_cmds:
                violations.append(
                    Violation(
                        type=ViolationType.WORKAROUND,
                        turn_index=rec.index,
                        severity="high",
                        rule="bash-interface-guess",
                        description=(
                            "Agent invoked a symbol or module that doesn't exist; "
                            "graph query (rai graph query) should precede first use"
                        ),
                        evidence=text[:200],
                    )
                )

            # bash-command-not-found (RC2/RC3): CLI tool not installed / wrong path
            if _COMMAND_NOT_FOUND_RE.search(text) and last_bash_cmds:
                violations.append(
                    Violation(
                        type=ViolationType.WORKAROUND,
                        turn_index=rec.index,
                        severity="medium",
                        rule="bash-command-not-found",
                        description=(
                            "Agent invoked a CLI command that isn't available in the environment; "
                            "check tool availability before use"
                        ),
                        evidence=text[:200],
                    )
                )

            # Track non-zero exits for retry detection
            if _BASH_NONZERO_RE.search(text):
                had_failure = True
            elif not _IMPORT_ERROR_RE.search(text) and not _COMMAND_NOT_FOUND_RE.search(
                text
            ):
                # Clean result clears the failure state
                had_failure = False

    return violations


# ── Public API ────────────────────────────────────────────────────────


def check_conformance(records: list[TurnRecord]) -> ConformanceReport:
    """Run all conformance detectors and return a combined report."""
    violations: list[Violation] = []
    violations.extend(detect_workarounds(records))
    violations.extend(detect_jidoka_violations(records))
    violations.extend(detect_tool_reliability_violations(records))
    violations.sort(key=lambda v: v.turn_index)
    return ConformanceReport(
        total_turns=len(records),
        violations=violations,
    )
