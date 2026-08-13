"""DefaultFleetPromptBuilder — implements FleetPromptBuilder (ADR §3 amended, D4/D10.b).

Assembles the full BRIEF.md a fleet subagent receives, replacing the old
`_build_agent_prompt()` one-liner (`subagent_dispatcher.py:121-144`). This is
the single seam for brief content (D4): governance preamble, skill essential
rules, the `[RAI:...]` header, the target worktree (D10.b — absolute path +
explicit enter-the-worktree instruction), task context, a Platform Matrix of
discovered pytest platform markers (RAISE-15767), a Touched Modules &
Contracts section from the knowledge graph (RAISE-15768), and the completion
protocol (D3).

*Constraint (type-level, D4):* `build()` receives only the non-secret
`run_id` — never `advance_token` or a `FleetRunBinding` — and the rendered
brief never contains the token value or an instruction to advance the
pipeline run itself. The DIRECTOR holds the token and advances on signal
(RAISE-13580, RAISE-14555, RAISE-15766).
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from raise_cli.pipeline.rai_header import build_rai_header

logger = logging.getLogger(__name__)

_GOVERNANCE_UNAVAILABLE = "(governance context unavailable)"

# --- RAISE-15767: Platform Matrix section -----------------------------------
#
# Discovers platform-keyed pytest markers already present in a worktree's
# test files so the rendered brief tells a fleet subagent which platforms
# its tests already account for -- preventing the RAISE-15658 class of bug
# (tests that pass only on the author's platform, e.g. Linux, and raise
# AttributeError on Windows/macOS). Best-effort and read-only: any discovery
# failure degrades to an empty report and a WARNING healthcheck status, it
# never raises out of `build()` (scope.md RISKS: "must not fail brief
# assembly on discovery errors").

#: Directory names skipped during marker discovery -- vendored/generated
#: trees are not "the worktree's tests" and would pollute the matrix.
_EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        ".venv-mcp",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        "dist",
        "build",
    }
)

#: `@pytest.mark.<platform>` decorator form, or the module-level
#: `pytestmark = pytest.mark.<platform>` / `pytestmark = [pytest.mark.<platform>, ...]`
#: form (RAISE-15767 quality-review R3 — both are real, common pytest syntax;
#: the bare-decorator pattern alone missed the module-level assignment form).
_NAMED_PLATFORM_MARKER_PATTERN = re.compile(
    r"(?:@|pytestmark\s*=\s*\[?\s*)pytest\.mark\.(darwin|linux|win32|windows|macos)\b"
)

#: Matches `pytest.mark.skipif(...)` / `pytest.mark.xfail(...)` calls whose
#: argument list references `sys.platform` or `os.name` -- the two builtin
#: conditionals used to key platform-specific skip/xfail behavior. Uses a
#: one-level balanced-paren atom (not `.` under DOTALL) so an intervening
#: call like `is_ci()` earlier in the argument list doesn't hide a real
#: platform conditional, WITHOUT crossing the decorator's own closing `)`
#: (RAISE-15767 quality-review R1 — the DOTALL `.` form matched platform
#: usage anywhere in the next 400 chars, including the test body after the
#: decorator ended, on decorators that had no platform conditional at all).
_PLATFORM_CONDITIONAL_PATTERN = re.compile(
    r"pytest\.mark\.(?:skipif|xfail)\s*\("
    r"(?:[^()]|\([^()]*\)){0,400}?(sys\.platform|os\.name)"
)

_PLATFORM_MARKER_DESCRIPTIONS: dict[str, str] = {
    "darwin": "macOS-specific behavior",
    "macos": "macOS-specific behavior",
    "linux": "Linux-specific behavior",
    "win32": "Windows-specific behavior",
    "windows": "Windows-specific behavior",
}


@dataclass(frozen=True)
class PlatformMarkerReport:
    """Result of scanning a worktree for platform-keyed pytest markers.

    named_markers: sorted unique `@pytest.mark.<platform>` names found.
    conditional_markers: sorted unique `sys.platform`/`os.name` conditionals
        found inside `skipif`/`xfail` calls.
    error: set (instead of raising) when discovery itself failed --
        degrades the healthcheck to WARNING rather than aborting the brief.
    """

    named_markers: tuple[str, ...] = ()
    conditional_markers: tuple[str, ...] = ()
    error: str | None = None

    @property
    def has_markers(self) -> bool:
        """True iff any named or conditional platform marker was found."""
        return bool(self.named_markers or self.conditional_markers)


def _iter_test_files(root: Path) -> Iterator[Path]:
    """Yield test/conftest `.py` files under `root`, pruning vendor dirs.

    Uses `os.walk` with an in-place `dirnames` filter rather than
    `Path.rglob("*.py")` (quality-review finding on RAISE-15767): `rglob`
    has no directory-pruning hook, so it fully descends into every
    subdirectory -- including a populated `.venv`/`node_modules` -- before
    the caller gets a chance to discard the result. `os.walk` lets us drop
    excluded directory names from `dirnames` before it recurses into them,
    so a vendor tree is never walked at all, not just filtered afterwards.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIR_NAMES]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            if (
                filename == "conftest.py"
                or filename.startswith("test_")
                or filename.endswith("_test.py")
            ):
                yield Path(dirpath) / filename


def _discover_platform_markers(worktree_path: str) -> PlatformMarkerReport:
    """Best-effort scan of `worktree_path`'s test files for platform markers.

    Returns an empty report (not an exception) for a missing/unresolved
    path -- mirrors `_load_governance_context`'s fail-fast-without-raising
    convention (D10.b's empty-string sentinel is valid here too).
    """
    if not worktree_path:
        return PlatformMarkerReport()
    root = Path(worktree_path)
    if not root.is_dir():
        return PlatformMarkerReport()
    try:
        named: set[str] = set()
        conditional: set[str] = set()
        for test_file in _iter_test_files(root):
            try:
                text = test_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            named.update(_NAMED_PLATFORM_MARKER_PATTERN.findall(text))
            conditional.update(_PLATFORM_CONDITIONAL_PATTERN.findall(text))
        return PlatformMarkerReport(
            named_markers=tuple(sorted(named)),
            conditional_markers=tuple(sorted(conditional)),
        )
    except Exception as exc:  # noqa: BLE001 — best-effort; brief assembly must not fail
        logger.warning(
            "FleetPromptBuilder: platform marker discovery failed for %s",
            worktree_path,
            exc_info=True,
        )
        return PlatformMarkerReport(error=str(exc))


def _platform_healthcheck(report: PlatformMarkerReport) -> tuple[str, str]:
    """Evaluate a `PlatformMarkerReport` into `(status, detail)`.

    Informational only (status is `OK` or `WARNING`) -- per scope.md DONE
    WHEN, a missing-marker or discovery-failure report logs a warning and
    proceeds, it never blocks brief assembly or dispatch.
    """
    if report.error is not None:
        return "WARNING", f"marker discovery failed: {report.error}"
    if not report.has_markers:
        return "WARNING", "no platform-specific test markers found in this worktree"
    return "OK", "platform-specific test markers found and readable"


def _render_platform_matrix(worktree_path: str) -> str:
    """Render the `## Platform Matrix` section (RAISE-15767, D4 seam)."""
    try:
        report = _discover_platform_markers(worktree_path)
    except Exception:  # noqa: BLE001 — brief assembly must never fail
        logger.warning(
            "FleetPromptBuilder: platform matrix rendering failed for %s",
            worktree_path,
            exc_info=True,
        )
        report = PlatformMarkerReport(error="platform matrix rendering failed")

    status, detail = _platform_healthcheck(report)
    if status != "OK":
        logger.warning(
            "FleetPromptBuilder: platform matrix healthcheck=%s for %s -- %s",
            status,
            worktree_path,
            detail,
        )

    platforms_line = (
        ", ".join(report.named_markers) if report.named_markers else "none detected"
    )

    marker_lines = [
        f"- @pytest.mark.{name} — "
        f"{_PLATFORM_MARKER_DESCRIPTIONS.get(name, 'platform-specific behavior')}"
        for name in report.named_markers
    ]
    marker_lines.extend(
        f"- skipif/xfail keyed on {cond} — platform-conditional test"
        for cond in report.conditional_markers
    )
    markers_block = (
        "\n".join(marker_lines)
        if marker_lines
        else "- none discovered in this worktree"
    )

    healthcheck_line = f"platform-specific test markers verified — {status}"
    if status != "OK":
        healthcheck_line += f" ({detail})"

    return (
        "## Platform Matrix\n\n"
        f"**Available test platforms:** {platforms_line}\n"
        "**Required test coverage:** tests must pass on every platform "
        "listed above; guard platform-specific behavior with the "
        "corresponding marker rather than assuming the build environment's "
        "platform (RAISE-15658).\n"
        f"**Platform-specific markers:**\n{markers_block}\n\n"
        f"**Healthcheck:** {healthcheck_line}"
    )


# --- RAISE-15768: Touched Modules & Contracts section -----------------------
#
# Queries the knowledge graph for `work_id` and renders each touched
# module's contract so a fleet subagent sees graph-observable impact, not
# just what commit history alone would suggest -- the RAISE-15565 class of
# scope miss (a commit touched module A, but the graph showed the true
# impact landed in module B's contract -- e.g. a Historia->Story mapping --
# and nothing surfaced that to the agent). Best-effort and read-only: any
# query failure degrades to a fallback line and a WARNING log, it never
# raises out of `build()` (scope.md RISKS: "must not fail brief assembly on
# discovery errors" -- same constraint RAISE-15767's platform matrix
# follows).

#: Max nodes rendered per brief -- keeps the section scannable (scope.md
#: EXPECTED: "bullet list ... so it is scannable") without truncating the
#: graph backend's own relevance ranking.
_GRAPH_QUERY_LIMIT = 8

_TOUCHED_MODULES_UNAVAILABLE = (
    "(no touched-module contracts found in the knowledge graph for this work item)"
)

#: Rendered content is truncated to this length so an oversized node
#: `content` field (e.g. a full docstring) can't blow up brief size.
_CONTRACT_CONTENT_SNIPPET_LEN = 160

#: Max length applied to `signature`/`node_id`/`label` when rendered into a
#: contract bullet (C1, RAISE-15768 quality-review) -- these three fields
#: were previously unbounded even though `content` was already capped.
_CONTRACT_FIELD_MAX_LEN = 160


def _sanitize_graph_text(value: str, max_len: int = _CONTRACT_FIELD_MAX_LEN) -> str:
    r"""Collapse whitespace to single spaces and cap length.

    Every field interpolated into a contract bullet is graph-sourced,
    untrusted text (C1, RAISE-15768 quality-review): a node's `content`,
    `signature`, `node_id`, or module `label` can contain arbitrary
    multi-line text pulled from source (docstrings, symbol names). Two
    concrete failure modes this closes:

    - Heading injection: a `\\n## <anything>` inside graph content would
      otherwise render as a top-level brief heading indistinguishable from
      a real governance section to a fleet subagent -- a prompt-injection
      channel via graph node content. Collapsing whitespace means no `\\n`
      survives into the rendered bullet, so this vector is structurally
      closed, not just filtered case-by-case.
    - Unbounded size: only `content` was previously length-capped;
      `signature`/`node_id`/`label` were not, so a pathological node could
      blow up brief size. All four fields are capped here.
    """
    collapsed = " ".join(value.split())
    if len(collapsed) <= max_len:
        return collapsed
    return collapsed[: max_len - 1] + "…"


def _query_graph_for_touched_modules(
    work_id: str, worktree_path: str
) -> list[dict[str, Any]]:
    """In-process knowledge-graph query for `work_id`'s touched modules.

    Reuses `get_graph_backend()` (`raise_cli.graph.query_backend`) -- the
    same in-process resolver the `raise_graph_query` MCP tool uses --
    instead of shelling out to `rai graph query` on every fleet dispatch.
    That resolver already falls back to a `rai graph` subprocess itself
    (`FilesystemGraphBackend`) when the in-process retrieval engine can't
    load an index, so this is not a new failure surface, just a faster
    common path for the case that matters here.

    Returns `[]` for an empty `work_id` without touching the backend at
    all -- mirrors `_discover_platform_markers`'s empty-input short circuit.
    Also returns `[]` (without querying) when `worktree_path` is non-empty
    but doesn't resolve to a real directory (R2, RAISE-15768
    quality-review): querying anyway would silently fall back to the
    graph backend's default root -- the DIRECTOR PROCESS's CWD -- instead
    of the intended worktree, a wrong-index risk. Mirrors
    `_discover_platform_markers`'s fail-fast-without-raising convention.
    Raises on backend failure; the caller (`_render_touched_modules_and_
    contracts`) is responsible for catching and degrading gracefully, same
    division of labor as `_discover_platform_markers` /
    `_render_platform_matrix`.
    """
    if not work_id:
        return []

    if worktree_path and not Path(worktree_path).is_dir():
        logger.warning(
            "FleetPromptBuilder: touched-module graph query skipped -- "
            "worktree_path=%s does not resolve to a directory",
            worktree_path,
        )
        return []

    from raise_cli.graph.query_backend import get_graph_backend

    root = Path(worktree_path) if worktree_path else None
    backend = get_graph_backend(root=root)
    # `GraphReadBackend.query()` is declared `-> dict[str, Any]`, but real
    # backends don't all honor that at runtime (mocks and ApiBackend may
    # return a list directly -- same caveat `raise_graph_query`'s MCP tool
    # normalizes against). Widened to `Any` here so the isinstance checks
    # below are real runtime guards, not statically-foregone conclusions.
    result: Any = asyncio.run(backend.query(work_id, _GRAPH_QUERY_LIMIT))

    if isinstance(result, list):
        return cast("list[dict[str, Any]]", result)
    results = result.get("results", []) if isinstance(result, dict) else []
    if isinstance(results, list):
        return cast("list[dict[str, Any]]", results)
    return []


def _contract_bullet(node: Any) -> str | None:
    """Render one graph-query result node into a scannable contract bullet.

    `node_id` is required -- a node without one can't be cited, so it is
    skipped rather than rendered as a bullet with a literal `None` id (the
    kind of defect a positive-only test suite would miss, per this epic's
    quality-review history on RAISE-15767's regex/detector defects).

    Prefers `metadata["signature"]` (the `SymbolNode` convention --
    `raise_core.graph.models.SymbolNode` -- populated for
    `@runtime_checkable` Protocol methods/classes discovered by `rai
    discover scan`) grouped under `metadata["module"]`; falls back to a
    truncated `content` snippet for nodes without a recorded signature
    (e.g. `ModuleNode`/`ComponentNode` concept nodes).
    """
    if not isinstance(node, dict):
        return None
    raw_node_id = node.get("node_id") or node.get("id")
    if not raw_node_id:
        return None
    node_id = _sanitize_graph_text(str(raw_node_id))

    metadata = node.get("properties")
    if not isinstance(metadata, dict):
        metadata = node.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    module = metadata.get("module") or node.get("node_type") or node.get("type")
    label = _sanitize_graph_text(str(module or "module"))
    signature = metadata.get("signature")
    if signature:
        signature = _sanitize_graph_text(str(signature))
        return f"- **{label}** — `{node_id}`: `{signature}`"

    content = str(node.get("content") or "").strip()
    if content:
        snippet = _sanitize_graph_text(content, _CONTRACT_CONTENT_SNIPPET_LEN)
        return f"- **{label}** — `{node_id}`: {snippet}"
    return f"- **{label}** — `{node_id}`"


def _drop_pipeline_advance_bullets(lines: list[str], work_id: str) -> list[str]:
    """D4 filter: drop any bullet whose text contains `pipeline_advance` (case-insensitive).

    Graph node content is untrusted input (C1, RAISE-15768 quality-review):
    the repo's own source mentions "pipeline_advance" in 8+ raise_cli
    files, so a populated graph queried for a fleet/pipeline work item can
    surface that literal substring into a rendered snippet -- violating
    the type-level constraint that the brief NEVER contains it
    (design.md:347-350, the exact invariant RAISE-15772 was built to
    guarantee). `_sanitize_graph_text` alone can't catch this (it bounds
    size and strips newlines, not specific substrings), so this is a
    dedicated second pass over the assembled bullets, mirroring the D4
    filter the rest of the builder already enforces. Dropped, not
    silently -- a warning is logged so the loss is traceable.
    """
    kept: list[str] = []
    for line in lines:
        if "pipeline_advance" in line.lower():
            logger.warning(
                "FleetPromptBuilder: dropped a touched-module contract "
                "bullet for work_id=%s -- contained the forbidden "
                "substring 'pipeline_advance' (D4)",
                work_id,
            )
            continue
        kept.append(line)
    return kept


def _render_touched_modules_and_contracts(work_id: str, worktree_path: str) -> str:
    """Render the `## Touched Modules & Contracts` section (RAISE-15768, D4 seam)."""
    try:
        nodes = _query_graph_for_touched_modules(work_id, worktree_path)
    except Exception:  # noqa: BLE001 — best-effort; brief assembly must not fail
        logger.warning(
            "FleetPromptBuilder: touched-module graph query failed for work_id=%s",
            work_id,
            exc_info=True,
        )
        # R1 (RAISE-15768 quality-review): render a fixed short message,
        # never the raw exception text -- `GraphQueryError` can carry
        # multi-line subprocess stderr, and the WARNING log above already
        # captures full exc_info for diagnosis.
        return (
            "## Touched Modules & Contracts\n\n"
            f"{_TOUCHED_MODULES_UNAVAILABLE} (graph query failed — see logs)"
        )

    contract_lines = [
        line for line in (_contract_bullet(node) for node in nodes) if line
    ]
    contract_lines = _drop_pipeline_advance_bullets(contract_lines, work_id)
    if not contract_lines:
        logger.warning(
            "FleetPromptBuilder: no touched-module contracts found for work_id=%s",
            work_id,
        )
        return f"## Touched Modules & Contracts\n\n{_TOUCHED_MODULES_UNAVAILABLE}"

    return (
        "## Touched Modules & Contracts\n\n"
        "Modules the knowledge graph associates with this work item, and "
        "the contracts they expose — review before changing behavior "
        "outside what commit history alone would suggest touching "
        "(RAISE-15565).\n\n" + "\n".join(contract_lines)
    )


_ESSENTIAL_RULES = (
    "- TDD Always — RED-GREEN-REFACTOR, no exceptions. Tests are the "
    "specification, not an afterthought.\n"
    "- Commit After Task — commit after each completed task, not just at "
    "story end.\n"
    "- Tests, type checks, and linting must all pass before any commit.\n"
    "- Follow the target skill's own phase order — do not skip a gate to "
    "move faster."
)


def _completion_protocol(work_id: str) -> str:
    """Render the D3 completion protocol — never names the advance command (D4)."""
    return (
        "When your work for this phase is complete:\n"
        "1. Finish the work — tests green, gates passing, a commit made.\n"
        "2. Call raise_task_complete(...) to record task completion.\n"
        f'3. Call fleet_signal(story_key="{work_id}", event="phase_complete", ...) '
        "to hand control back to the fleet director.\n\n"
        "You hold no authority to move this pipeline run to its next phase "
        "yourself — do not attempt it. The fleet director owns that step and "
        "performs it after receiving your phase_complete signal."
    )


def _derive_phase(skill: str) -> str:
    """Best-effort phase id from a skill name — last hyphen-separated segment.

    RaiSE skill names follow `rai-<worktype>-<phase>` (e.g.
    "rai-story-implement" -> "implement", "rai-bugfix-fix" -> "fix"). `build()`
    has no separate phase parameter (D4's four-parameter signature), so this
    is the only source for the header's `phase=` field.
    """
    if not skill:
        return "unknown"
    return skill.rsplit("-", 1)[-1]


def _flatten_dict_payload(payload: dict[str, Any]) -> list[str]:
    """Bullet-render a section payload shaped like `{key: value | [value, ...]}`."""
    lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, list):
            lines.extend(f"- {key}: {item}" for item in value)
        elif value not in (None, ""):
            lines.append(f"- {key}: {value}")
    return lines


def _flatten_list_payload(payload: list[Any]) -> list[str]:
    """Bullet-render a section payload shaped like `[{"id": ..., "content": ...}, ...]`."""
    lines: list[str] = []
    for item in payload:
        if isinstance(item, dict):
            ident = item.get("id", "")
            body = item.get("content", item)
            lines.append(f"- {ident}: {body}" if ident else f"- {body}")
        else:
            lines.append(f"- {item}")
    return lines


def _flatten_context_dict(content: dict[str, Any]) -> str:
    """Render a structured (Api/Postgres) session-context dict into readable text.

    C2 (RAISE-15772 quality-review): `get_session_context_backend` returns
    `ApiSessionContextBackend` whenever `RAISE_SERVER_URL` is set — the real
    fleet-hosting environment — and that backend's `content` is a dict by
    contract (`session/context_backend.py:33-36`), never a plain string.
    `PostgresSessionContextBackend` (`raise_server/session/context_backend_db.py`)
    produces the same shape server-side: `{section: {...} | [...]}`, e.g.
    `{"governance": {"governed_projects": [...], "evaluation_rules": [...]},
    "behavioral": [{"id": ..., "content": ..., "context": [...]}]}`.

    Mirrors the bullet-list style `session/bundle_formatters.py`'s
    `format_governance_primes`/`format_primes` use for the Filesystem
    backend's local-graph rendering — same visual shape, different data
    source — so a subagent's governance section reads consistently
    regardless of which backend served it.
    """
    parts: list[str] = []
    for section, payload in content.items():
        if isinstance(payload, dict):
            body_lines = _flatten_dict_payload(payload)
        elif isinstance(payload, list):
            body_lines = _flatten_list_payload(payload)
        elif payload not in (None, ""):
            body_lines = [f"- {payload}"]
        else:
            body_lines = []
        if body_lines:
            title = f"# {section.replace('_', ' ').title()}"
            parts.append("\n".join([title, *body_lines]))
    return "\n\n".join(parts)


def _load_governance_context(worktree_path: str) -> str:
    """Default `context_loader` — the `rai session context -s governance,behavioral` pattern.

    Per D4, via the same in-process backend `raise_session_context` uses.

    Guards on `Path.is_dir()` before touching the backend: the real backend
    shells out to `rai session context` (`FilesystemSessionContextBackend`),
    and there is no point spawning that subprocess against a path that isn't
    even a real directory — fails fast instead of eating a subprocess
    round-trip (and keeps callers over an unresolved/fake path hermetic).
    Any failure degrades to a marker string rather than raising — brief
    assembly must never fail because governance context was unavailable.

    C2 (RAISE-15772 quality-review): `content` is NOT always a string. Under
    `ApiSessionContextBackend`/`PostgresSessionContextBackend` (whenever
    `RAISE_SERVER_URL` or the HTTP transport is active — the real
    fleet-hosting environment) it is a structured dict, flattened via
    `_flatten_context_dict` rather than silently degrading to the
    placeholder. Every path that ends in the placeholder logs a warning so
    this class of defect (previously silent) is observable.
    """
    if not worktree_path or not Path(worktree_path).is_dir():
        return _GOVERNANCE_UNAVAILABLE
    try:
        from raise_cli.session.context_backend import get_session_context_backend

        backend = get_session_context_backend(cwd=worktree_path)
        result = asyncio.run(backend.bundle(["governance", "behavioral"]))
        if result.get("status") == "ok":
            content = result.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
            if isinstance(content, dict) and content:
                flattened = _flatten_context_dict(content)
                if flattened.strip():
                    return flattened.strip()
            logger.warning(
                "FleetPromptBuilder: governance context degraded to "
                "placeholder for %s — status=ok but content (type=%s) "
                "yielded no renderable text",
                worktree_path,
                type(content).__name__,
            )
            return _GOVERNANCE_UNAVAILABLE
        logger.warning(
            "FleetPromptBuilder: governance context degraded to placeholder "
            "for %s — backend returned status=%r",
            worktree_path,
            result.get("status"),
        )
        return _GOVERNANCE_UNAVAILABLE
    except Exception:  # noqa: BLE001 — best-effort; brief assembly must not fail
        logger.warning(
            "FleetPromptBuilder: governance context load failed for %s",
            worktree_path,
            exc_info=True,
        )
        return _GOVERNANCE_UNAVAILABLE


class DefaultFleetPromptBuilder:
    """Implements `FleetPromptBuilder` (raise_core.fleet.protocols) — D4/D10.b.

    `context_loader` is injectable so callers (and tests) can avoid the real
    `rai session context` subprocess; defaults to `_load_governance_context`.
    """

    def __init__(self, context_loader: Callable[[str], str] | None = None) -> None:
        self._context_loader = context_loader or _load_governance_context

    def build(
        self,
        work_id: str,
        skill: str,
        run_id: str,
        worktree_path: str,
    ) -> str:
        """Assemble and return the full BRIEF.md text for one subagent dispatch.

        Section order (D4): [RAI:...] header, Governance Context, Work
        Directory Setup (D10.b), Task Definition, Platform Matrix
        (RAISE-15767), Touched Modules & Contracts (RAISE-15768), Skill
        Essential Rules, Completion Protocol (D3).

        Raises:
            ValueError: R2 (RAISE-15772 quality-review) — `worktree_path` is
                non-empty but not absolute. Rendered verbatim into `cd
                {worktree_path}` below; a relative path there is a broken
                instruction a subagent would silently follow into the wrong
                directory. This is the seam RAISE-15767/15768 reuse, so it
                fails loudly here rather than emitting bad output.
        """
        if worktree_path and not Path(worktree_path).is_absolute():
            raise ValueError(
                f"FleetPromptBuilder.build(): worktree_path must be an "
                f"absolute path, got {worktree_path!r} — refusing to render "
                "a broken `cd` instruction"
            )

        from raise_cli._agent_session import discover_agent_session_id

        phase = _derive_phase(skill)
        parent_session = discover_agent_session_id()

        header = build_rai_header(
            type="fleet",
            skill=skill,
            phase=phase,
            run_id=run_id or None,
            parent_session=parent_session,
        )
        if not header and run_id:
            # R1 (RAISE-15772 quality-review): a live brief (real run_id)
            # that ends up headerless — usually parent_session resolving to
            # None (no session env vars, unrecognized PPID chain) — is a
            # silent classification gap for JSONL transcript tooling.
            # Observable now instead of a quiet no-header degrade.
            logger.warning(
                "FleetPromptBuilder: [RAI:] header omitted for a live brief "
                "(run_id=%s, skill=%s, work_id=%s) — parent_session or "
                "another required header field could not be resolved",
                run_id,
                skill,
                work_id,
            )

        try:
            governance = self._context_loader(worktree_path)
        except Exception:  # noqa: BLE001 — brief assembly must never fail
            logger.warning(
                "FleetPromptBuilder: context_loader raised for %s",
                worktree_path,
                exc_info=True,
            )
            governance = _GOVERNANCE_UNAVAILABLE

        sections: list[str] = []
        if header:
            sections.append(header)
        sections.append(f"## Governance Context\n\n{governance}")
        sections.append(
            "## Work Directory Setup\n\n"
            f"cd {worktree_path}\n\n"
            "Enter this worktree before making any changes. All file "
            "operations for this task MUST happen inside this absolute path."
        )
        sections.append(
            "## Task Definition\n\n"
            f"Work item: {work_id}\n"
            f"Skill: {skill}\n"
            f"Phase: {phase}"
        )
        try:
            platform_matrix = _render_platform_matrix(worktree_path)
        except Exception:  # noqa: BLE001 — brief assembly must never fail
            logger.warning(
                "FleetPromptBuilder: platform matrix section failed to render for %s",
                worktree_path,
                exc_info=True,
            )
            platform_matrix = (
                "## Platform Matrix\n\n"
                "**Healthcheck:** platform-specific test markers verified — "
                "WARNING (section rendering failed)"
            )
        sections.append(platform_matrix)
        try:
            touched_modules = _render_touched_modules_and_contracts(
                work_id, worktree_path
            )
        except Exception:  # noqa: BLE001 — brief assembly must never fail
            logger.warning(
                "FleetPromptBuilder: touched modules & contracts section "
                "failed to render for work_id=%s",
                work_id,
                exc_info=True,
            )
            touched_modules = (
                "## Touched Modules & Contracts\n\n"
                f"{_TOUCHED_MODULES_UNAVAILABLE} (section rendering failed)"
            )
        sections.append(touched_modules)
        sections.append(f"## Skill Essential Rules\n\n{_ESSENTIAL_RULES}")
        sections.append(f"## Completion Protocol\n\n{_completion_protocol(work_id)}")

        return "\n\n".join(sections) + "\n"
