"""Pipeline MCP tools — pipeline_list/start/advance/pause/cancel/restore/status/runs."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import shlex
import shutil
import tomllib
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.compat import get_rai_executable
from raise_cli.onboarding.profile import load_developer_profile
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only
from raise_cli.pipeline._mcp_instance import mcp
from raise_cli.pipeline._telemetry import emit_phase_transition
from raise_cli.pipeline.epic_story_iteration import pending_epic_stories
from raise_cli.pipeline.loader import PipelineError, PipelineLoader, create_loader
from raise_cli.pipeline.run_store import OptimisticLockError, get_run_store
from raise_cli.session.open_service import commits_behind, get_worktree_merge_target
from raise_cli.telemetry.audit import emit_hitl_decision
from raise_cli.telemetry.phase_report import (
    PhaseFinishReport,
    format_phase_summary,
    phase_finish_report,
)
from raise_cli.telemetry.session_tokens import find_cc_jsonl_by_session_id
from raise_core.workflow.models import PipelineDefinition

if TYPE_CHECKING:
    from raise_cli.release_preflight import ReleasePreflightResult

_log = logging.getLogger(__name__)

# Strong references to fire-and-forget background tasks prevent premature GC
_BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


def is_foreign_live_run(run: dict[str, Any]) -> tuple[bool, str]:
    """Check if *run* is owned by a live session that is NOT the caller (RAISE-15802).

    Returns ``(True, owner_description)`` when the run's worktree lease is live
    and belongs to a different agent session.  Fail-open: any lookup failure
    returns ``(False, "")``.
    """
    meta = run.get("metadata") or {}
    locked_wt = meta.get("locked_worktree")
    owner_session = meta.get("agent_session_id")
    if not locked_wt or not owner_session:
        return False, ""

    caller_session = discover_agent_session_id()
    if caller_session and owner_session == caller_session:
        return False, ""

    try:
        from raise_cli.pipeline.branch_guard import lease_is_live
        from raise_cli.storage.leases import SqliteLeaseStore
        from raise_cli.storage.worktrees import (
            SqliteWorktreeStore,
            WorktreeNotFoundError,
        )

        wt_path = Path(locked_wt)
        try:
            wt = SqliteWorktreeStore(wt_path).get_by_path(locked_wt)
        except WorktreeNotFoundError:
            return False, ""
        lease = SqliteLeaseStore(wt_path).get(wt.worktree_id)
        if lease is None or not lease_is_live(lease):
            return False, ""
        return True, (
            f"session '{lease.session_id}' in worktree {locked_wt} "
            f"(pid {lease.pid}, heartbeat {lease.heartbeat_at})"
        )
    except Exception:  # noqa: BLE001 — fail-open (ADR-094)
        _log.debug("ownership check failed open", exc_info=True)
        return False, ""


def _get_event_emitter(project_root: Path | None = None) -> Any:
    """Lazy EventEmitter with UnifiedEmitter for HTTP delivery (S3672.1).

    Imported lazily to avoid heavy imports at module level (MCP subprocess startup).
    Loads RAISE env vars from ~/.bashrc because CC spawns MCP subprocesses as
    non-interactive shells where ~/.bashrc guards return early.

    ``project_root`` anchors the emitter to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD resolution.
    """
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.hooks.emitter import EventEmitter
    from raise_cli.telemetry.emitter import UnifiedEmitter, load_raise_env_from_bashrc

    load_raise_env_from_bashrc()
    emitter = EventEmitter()
    hook = UnifiedEmitter(project_root=resolve_checkout_root(project_root))
    emitter.register("pipeline:phase_entered", hook.handle)
    return emitter


def _detect_mission_id() -> str:
    return ""


def _emit_lifecycle(
    pipeline_name: str,
    issue_id: str,
    event: str,
    phase_id: str,
    cwd: str | Path | None = None,
) -> None:
    """WorkLifecycle as a handler side-effect — S7884.5/S7884.6 (K3).

    Thin alias over the shared helper so the engine emits on every
    phase transition without LLM turns. Callers suppress failures.

    ``cwd`` is the run's own checkout (RAISE-15986). The engine runs in
    the MCP server process, so omitting it makes git correlation and the
    checkout-scoped ``work:lifecycle`` hooks resolve against the server's
    directory rather than the run's worktree.
    """
    from raise_cli.telemetry.emit_work import emit_work_lifecycle

    emit_work_lifecycle(
        pipeline_name,
        issue_id,
        event,
        phase_id,
        cwd=str(cwd) if cwd is not None else None,
    )


# Graph index path (resolved once per query from CWD)
_GRAPH_INDEX = Path(".raise") / "rai" / "memory" / "index.json"


# Pipeline run persistence — S1962.7.
#
# Runs are persisted via the `PipelineRunStore` Protocol (ADR-053) resolved
# per-transport by `get_run_store()` (imported at top):
#   - stdio (local)            → SqliteRunStore (WAL), project SQLite DB
#   - HTTP (Rovo multi-tenant) → PostgresRunStore, scoped by (org_id, member_id)
#
# The `_runs` in-memory dict + `_RunStore` class + `_save_run` helper were
# removed in S1962.7 — see `run_store.py` for the replacement and
# `work/post-webinar/README.md` for the cache retrofit note.

_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "shall",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "not",
        "no",
        "if",
        "when",
        "than",
        "so",
        "very",
        "just",
        "also",
        "then",
        "only",
        "all",
        "each",
        "use",
        "using",
        "used",
        "see",
        "scope",
        "done",
    }
)


def _extract_domain_entities(
    issue_id: str, search_root: Path | None = None
) -> list[str]:
    """Extract domain keywords from story artifacts.

    Reads scope.md, story.md, design.md for the issue.
    Falls back to issue_id parts when no docs found.

    Args:
        issue_id: Issue key for glob matching.
        search_root: Directory to search from. Defaults to the active
            checkout root (worktree-local, not the main checkout).

    Returns keywords sorted by frequency (most common first).
    """
    import re
    from collections import Counter

    if search_root is None:
        from raise_cli.config.paths import resolve_checkout_root

        search_root = resolve_checkout_root()
    root = search_root

    # Extract numeric part of issue_id for glob matching
    issue_num = re.sub(r"[^0-9]", "", issue_id)

    # Search for story docs in priority order
    text = ""
    for suffix in ("scope.md", "story.md", "design.md"):
        pattern = f"**/*{issue_num}*-{suffix}" if issue_num else f"**/*-{suffix}"
        matches = list(root.glob(pattern))
        if matches:
            text += matches[0].read_text()
            break  # Use highest priority doc

    if not text:
        # Fallback: use issue_id parts as keywords
        parts = re.split(r"[-_]", issue_id)
        return [p for p in parts if len(p) > 1]

    # Extract words: split on non-alphanumeric, filter
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in _STOP_WORDS and len(w) > 2]

    # Return top keywords by frequency
    counter = Counter(words)
    return [word for word, _ in counter.most_common(15)]


def _loader(cwd: str = "") -> PipelineLoader:
    """Build a pipeline loader rooted at the calling worktree.

    Resolves the pipeline-definition project root from the caller's ``cwd``
    (the invoking worktree), not the MCP server process cwd — mirrors the
    already-correct ``_resolve_skill_model`` pattern (RAISE-11134). Falls
    back to ``resolve_checkout_root()``'s own ``Path.cwd()`` default only
    when no caller ``cwd`` is available.
    """
    from raise_cli.config.paths import resolve_checkout_root

    return create_loader(project_root=resolve_checkout_root(Path(cwd) if cwd else None))


def _git_common_dir(path: Path) -> Path | None:
    """Return the git common dir for ``path`` (shared across all worktrees)."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = (path / p).resolve()
    return p.resolve()


def _check_mcp_worktree_identity(cwd: str) -> dict[str, str] | None:
    """Reject a worktree call routed to an MCP server asserted for another repo.

    Allows worktrees of the SAME repository (RAISE-15781): compares
    ``git rev-parse --git-common-dir`` which is shared across all worktrees
    of one repo, instead of ``--show-toplevel`` which differs per worktree.

    Assertion sources (D4, S15457.2): parsed ``--project`` argv, else
    ``RAISE_PROJECT_ROOT`` env, else none. The server process CWD is NEVER
    an assertion source — post-chdir-removal it is arbitrary spawn state.
    """
    if not cwd:
        return None
    asserted = _caller_context.get_asserted_root()
    if asserted is None:
        return None

    from raise_cli.config.paths import resolve_checkout_root

    caller_root = resolve_checkout_root(Path(cwd)).resolve()
    server_root = asserted.resolve()
    if caller_root == server_root:
        return None

    caller_common = _git_common_dir(Path(cwd))
    server_common = _git_common_dir(asserted)
    if caller_common and server_common and caller_common == server_common:
        return None

    return {
        "status": "rejected",
        "reason": "worktree_mismatch",
        "caller_root": str(caller_root),
        "server_root": str(server_root),
    }


# Phase-typed retrieval configuration (research: context-injection-sota)
# Different phases need different context types (MVC principle).
PHASE_RETRIEVAL: dict[str, list[dict[str, Any]]] = {
    "design": [
        {"types": ["pattern"], "limit": 3},
        {"types": ["module"], "limit": 2},
        {"types": ["decision"], "limit": 2},
    ],
    "plan": [
        {"types": ["guardrail"], "limit": 2},
        {"types": ["pattern"], "limit": 3},
    ],
    "implement": [
        {"types": ["pattern"], "limit": 3},
        {"types": ["module"], "limit": 2},
    ],
    "review": [
        {"types": ["pattern"], "limit": 3},
        {"types": ["guardrail"], "limit": 2},
    ],
    "architecture-review": [
        {"types": ["pattern"], "limit": 3},
        {"types": ["module"], "limit": 2},
        {"types": ["decision"], "limit": 2},
    ],
    "quality-review": [
        {"types": ["pattern"], "limit": 2},
        {"types": ["guardrail"], "limit": 3},
    ],
}

# Token budget for context injection (MVC: smallest high-signal set)
MAX_CONTEXT_TOKENS = 2000


def _resolve_pipeline_scorer(root: Path | None = None) -> Any:
    """Resolve SemanticScorer for pipeline context (S-HFNR.3). None on failure.

    ``root`` anchors the cartridge scan to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD resolution.
    """
    try:
        from raise_cli.config.server import get_server_credentials
        from raise_core.graph.scorers import resolve_semantic_scorer

        creds = get_server_credentials()
        server_url = creds[0] if creds else None
        api_key = creds[1] if creds else None
        cartridges_root = (root or Path.cwd()) / ".raise" / "cartridges"
        embeddings_dirs = (
            [
                d
                for d in sorted(cartridges_root.glob("*/instances"))
                if (d / "embeddings.npy").exists()
            ]
            if cartridges_root.is_dir()
            else []
        )
        return resolve_semantic_scorer(
            embeddings_dirs=embeddings_dirs,
            server_url=server_url,
            api_key=api_key,
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("SemanticScorer resolution failed", exc_info=True)
        return None


def _retrieve_for_spec(
    graph: Any,
    query_str: str,
    limit: int,
    type_filter: list[str] | None,
    semantic_scorer: Any,
) -> list[tuple[str, str, str]]:
    """Run the federation orchestrator and return (id, type, content) tuples.

    Uses ``federated_retrieve_from_graph`` (ADR-103): federates across cartridges
    when the graph holds >1, falls back to single-cartridge ``retrieve()`` otherwise.
    The tuple-building / type-filter loop below is unchanged.
    """
    from raise_cli.graph.query_backend import NeutralDomainAdapter
    from raise_core.graph.retrieval.federation import federated_retrieve_from_graph

    overfetch = limit * 3 if type_filter else limit
    result = federated_retrieve_from_graph(
        graph,
        query_str,
        NeutralDomainAdapter(),
        top_k=overfetch,
        semantic_scorer=semantic_scorer,
    )
    nodes: list[tuple[str, str, str]] = []
    for sn in result.nodes:
        if type_filter and sn.node.type not in type_filter:
            continue
        nodes.append((sn.node.id, str(sn.node.type), sn.node.content))
        if len(nodes) >= limit:
            break
    return nodes


def _build_phase_context(
    phase_id: str,
    skill: str,
    run: dict[str, Any],
    context_spec: list[dict[str, Any]] | None = None,
    search_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Build phase-aware context from knowledge graph.

    3-stage pipeline (from SOTA research):
    1. Extract domain entities from story docs
    2. Run phase-typed queries with entity seeds (from YAML spec or fallback)
    3. Cap at token budget (MVC)

    Args:
        phase_id: Phase being entered (determines retrieval profile).
        skill: Name of the skill about to execute — surfaces skill-specific context.
        run: Persisted PipelineRun dict; supplies issue_id, prior phase metadata.
        context_spec: Declarative graph queries from YAML ``context.graph``.
            If None, falls back to ``PHASE_RETRIEVAL`` hardcoded config.
        search_root: Directory to search for graph index and story docs.
            Defaults to the active checkout root (worktree-local, not the
            main checkout).

    Returns list of graph node dicts, or empty list on degradation.
    """
    if search_root is None:
        from raise_cli.config.paths import resolve_checkout_root

        search_root = resolve_checkout_root()
    root = search_root
    graph_path = root / _GRAPH_INDEX
    if not graph_path.exists():
        return []

    try:
        from raise_cli.graph.backends import get_active_backend

        backend = get_active_backend(path=graph_path)
        graph = backend.load()
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("Graph load failed", exc_info=True)
        return []

    # Resolve semantic scorer for hybrid retrieval (S-HFNR.3)
    semantic_scorer = _resolve_pipeline_scorer(root)

    # Stage 1: Extract domain entities
    issue_id: str = run.get("issue_id", "")
    entities = _extract_domain_entities(issue_id, search_root=root)
    query_str = " ".join(entities) if entities else f"{phase_id} {skill}"

    # Stage 2: Phase-typed retrieval — YAML spec or fallback
    specs = (
        context_spec
        if context_spec is not None
        else PHASE_RETRIEVAL.get(phase_id, [{"types": [], "limit": 5}])
    )
    results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    total_chars = 0

    for spec in specs:
        type_filter: list[str] | None = spec.get("types") or None
        limit = spec.get("limit", 3)
        try:
            nodes = _retrieve_for_spec(
                graph, query_str, limit, type_filter, semantic_scorer
            )
            for node_id, node_type, content in nodes:
                if node_id in seen_ids:
                    continue
                content = content[:200]
                # Stage 3: Token budget
                total_chars += len(content)
                if total_chars > MAX_CONTEXT_TOKENS * 4:  # ~4 chars per token
                    break
                seen_ids.add(node_id)
                results.append(
                    {
                        "id": node_id,
                        "type": node_type,
                        "content": content,
                    }
                )
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            _log.debug("Graph query failed for spec=%s", spec, exc_info=True)
            continue

    return results


_MAX_ARTIFACT_MATCHES = 5  # Cap glob results per pattern to avoid response bloat


def _get_artifact_store(root: Path | None = None) -> Any:
    """Lazy-load ArtifactStore for SQLite-based artifact validation.

    ``root`` anchors the project DB to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD resolution.
    """
    from raise_cli.artifacts.store import ArtifactStore
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    checkout = resolve_checkout_root(root)
    conn = get_project_db(checkout)
    create_all(conn)
    return ArtifactStore(conn, project_id=get_project_id(checkout))


def _substitute_issue_vars(pattern: str, issue_id: str) -> str:
    """Replace ``{issue_id}`` and ``{issue_num}`` template vars in a glob pattern."""
    import re as _re

    if not issue_id:
        return pattern
    issue_num = _re.sub(r"[^0-9]", "", issue_id)
    result = pattern.replace("{issue_id}", issue_id)
    if issue_num:
        result = result.replace("{issue_num}", issue_num)
    return result


def _recency_threshold(phase_started_at: str) -> float | None:
    """Parse ``phase_started_at`` ISO string into a POSIX timestamp, or None."""
    import contextlib

    ts: float | None = None
    if phase_started_at:
        with contextlib.suppress(ValueError, TypeError):
            ts = datetime.fromisoformat(phase_started_at).timestamp()
    return ts


def _check_glob_req(
    req: dict[str, Any],
    root: Path,
    issue_id: str,
    started_ts: float | None,
) -> tuple[bool, list[str]]:
    """Check a single glob validates entry. Returns (found_any, found_paths)."""
    import re

    configured_patterns = req.get("patterns")
    if isinstance(configured_patterns, list):
        patterns = [
            pattern
            for pattern in configured_patterns
            if isinstance(pattern, str) and pattern
        ]
    else:
        configured_pattern = req.get("pattern")
        patterns = (
            [configured_pattern]
            if isinstance(configured_pattern, str) and configured_pattern
            else []
        )

    matches: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        raw_pattern = _substitute_issue_vars(pattern, issue_id)
        for match in root.glob(raw_pattern):
            if match not in seen:
                seen.add(match)
                matches.append(match)
    if not matches:
        return False, []
    # Issue scoping (S7884.6): broad globs like **/*-plan.md match every
    # epic in the repo — when matches carrying this run's issue number
    # exist, inject only those. Existence above is already decided.
    issue_num = re.sub(r"[^0-9]", "", issue_id)
    if issue_num:
        # Digit boundaries: issue 12 must not claim s112.5 artifacts (AR).
        bounded = re.compile(rf"(?<!\d){issue_num}(?!\d)")
        scoped = [m for m in matches if bounded.search(m.name)]
        if scoped:
            matches = scoped
    # Filter by recency for previous_artifacts; existence uses unfiltered matches.
    if started_ts is not None:
        recent = [m for m in matches if m.stat().st_mtime >= started_ts]
        return True, [str(m) for m in recent[:_MAX_ARTIFACT_MATCHES]]
    return True, [str(m) for m in matches[:_MAX_ARTIFACT_MATCHES]]


def _validate_artifacts(
    validates: list[dict[str, Any]],
    search_root: Path | None = None,
    *,
    issue_id: str = "",
    phase_started_at: str = "",
) -> tuple[bool, list[dict[str, Any]], list[str]]:
    """Check artifact existence via glob or SQLite store.

    Supports three entry formats in ``validates``:
    - ``{"pattern": glob, "description": label}`` — file glob check
    - ``{"patterns": [glob, ...], "description": label}`` — any file glob check
    - ``{"store": "sqlite", "type": artifact_type, "description": label}`` — SQLite check

    Args:
        validates: List of validation entries (glob or SQLite).
        search_root: Directory to resolve globs from. Defaults to the active
            checkout root (worktree-local, not the main checkout).
        issue_id: Issue key for SQLite checks and ``{issue_id}``/``{issue_num}``
            template substitution in glob patterns.
        phase_started_at: ISO timestamp of when the phase started. When set,
            ``found`` only includes files modified after this time — preventing
            artifacts from prior stories polluting ``previous_artifacts``.
            The existence check (``all_present``) is unaffected.

    Returns (all_present, missing_list, found_paths).
    """
    if search_root is None:
        from raise_cli.config.paths import resolve_checkout_root

        search_root = resolve_checkout_root()
    root = search_root
    missing: list[dict[str, Any]] = []
    found: list[str] = []
    artifact_store: Any = None
    started_ts = _recency_threshold(phase_started_at)

    for req in validates:
        if req.get("store") == "sqlite":
            if artifact_store is None:
                artifact_store = _get_artifact_store(root)
            artifact_type = req.get("type", "")
            from raise_cli.artifacts.identity import resolve_artifact_identity

            if not issue_id:
                missing.append(req)
                continue
            artifact_identity = resolve_artifact_identity(issue_id, root)
            matched_identity = (
                artifact_identity
                if artifact_store.exists(artifact_identity, artifact_type)
                else issue_id
                if artifact_identity != issue_id
                and artifact_store.exists(issue_id, artifact_type)
                else None
            )
            if matched_identity is None:
                missing.append(req)
            else:
                found.append(f"sqlite:{matched_identity}:{artifact_type}")
        else:
            ok, paths = _check_glob_req(req, root, issue_id, started_ts)
            if ok:
                found.extend(paths)
            else:
                missing.append(req)
    return len(missing) == 0, missing, found


def _resolve_skill_model(
    skill: str | None,
    cwd: str = "",
    phase_path: str | None = None,
    phase_model: str | None = None,
) -> str | None:
    """Best-effort model lookup from skill frontmatter.

    Resolves the skills directory from the calling worktree (``cwd``), not
    the MCP server process cwd — mirrors the already-correct
    ``fleet/subagent_dispatcher.py`` pattern (RAISE-11134).
    """
    if not skill and phase_path is None and phase_model is None:
        return None
    try:
        from raise_cli.config.paths import resolve_checkout_root
        from raise_cli.pipeline.skill_model import parse_skill_model

        root = resolve_checkout_root(Path(cwd) if cwd else None)
        return parse_skill_model(
            skill or "__phase__",
            root / ".claude" / "skills",
            phase_path=phase_path,
            phase_model=phase_model,
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None


_CC_HARNESSES = frozenset({"claude", "claude-code"})


def _non_cc_instruction(
    skill: str,
    issue_id: str,
    effective_harness: str,
    model: str | None,
    skill_base: Path | None,
) -> str:
    """Build the dispatch instruction for non-Claude-Code harnesses.

    Attempts to use AgentRuntimeAdapter for known runtimes (codex/kimi/hermes).
    Falls back to the legacy ``Execute skill:`` format when:
    - skill_base is not provided
    - the skill file is missing
    - the harness is not a known runtime (e.g. ``cursor``)
    """
    if skill_base is not None:
        try:
            from raise_cli.pipeline.agent_runtime_adapter import AgentRuntimeAdapter

            adapter = AgentRuntimeAdapter.from_harness(effective_harness, skill_base)
            base = adapter.build_phase_instruction(skill, args=issue_id)
            if model:
                base += f"\nRequested model: {model}"
            return base
        except (ValueError, FileNotFoundError):
            pass  # fall through to legacy format

    clean = skill.removeprefix("rai-")
    base = f"Execute skill: /rai-{clean} {issue_id}"
    if model:
        base += f"\nRequested model: {model}"
    return base


def _resolve_harness(phase_dict: dict[str, Any], cwd: str) -> str | None:  # noqa: ARG001 — cwd reserved for future per-project resolution
    """Resolve the effective dispatch harness for a phase.

    Precedence:
    1. ``phase_dict["harness"]`` — phase-level override from YAML.
    2. ``DeveloperProfile.harness`` — user's persistent default.
    3. ``None`` — caller falls back to Claude Code default (no regression).

    Args:
        phase_dict: Serialised phase dict from the run store.
        cwd: Project working directory (reserved for future per-project lookup).

    Returns:
        Harness string (e.g. ``"cursor"``, ``"codex"``) or ``None``.
    """
    phase_harness: str | None = phase_dict.get("harness")
    if phase_harness is not None:
        return phase_harness
    profile = load_developer_profile()
    if profile is not None:
        return profile.harness
    return None


def _phase_instruction(
    skill: str | None,
    issue_id: str,
    model: str | None = None,
    *,
    harness: str | None = None,
    run_id: str | None = None,
    phase_id: str | None = None,
    parent_session: str | None = None,
    skill_base: Path | None = None,
) -> str:
    """Build the instruction string for a phase."""
    if not skill:
        return "Complete phase manually (no skill configured)"
    clean = skill.removeprefix("rai-")
    effective_harness = (harness or "claude-code").lower()
    if effective_harness in _CC_HARNESSES:
        if model:
            base = f'Spawn Agent(model="{model}") to execute skill: /rai-{clean} {issue_id}'
        else:
            base = f"Execute skill: /rai-{clean} {issue_id}"
    else:
        base = _non_cc_instruction(
            skill, issue_id, effective_harness, model, skill_base
        )
    from raise_cli.pipeline.rai_header import build_rai_header

    header = build_rai_header(
        type="pipeline",
        skill=skill,
        phase=phase_id,
        run_id=run_id,
        parent_session=parent_session,
    )
    if header:
        session_binding = ""
        if skill == "rai-bugfix-review" and parent_session:
            session_binding = (
                "\nPipeline session binding: for `rai gate ar-attest --gate "
                "gate-ar-bugfix`, set RAISE_AGENT_SESSION_ID to the exact "
                "`parent_session` value in the [RAI:] header. The close gate "
                "will verify that same session-scoped marker."
            )
        elif skill == "rai-story-review" and parent_session:
            session_binding = (
                "\nPipeline session binding: for `rai gate ar-attest --gate "
                "gate-ar-story`, set RAISE_AGENT_SESSION_ID to the exact "
                "`parent_session` value in the [RAI:] header. The close gate "
                "will verify that same session-scoped marker."
            )
        return f"{header}\n{base}{session_binding}"
    return base


def _phase_execution_contract(
    phase: dict[str, Any], resolved_model: str | None = None
) -> dict[str, Any]:
    """Return the immutable execution fields an orchestrator must observe."""
    return {
        "model": (
            resolved_model
            if resolved_model is not None
            else phase.get("resolved_model")
        ),
        "max_budget_usd": phase.get("max_budget_usd", 5.0),
        "phase_path": phase.get("phase_path"),
    }


def _restored_phase_dispatch(
    run: dict[str, Any], current: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Rebuild dispatch data from the immutable phase snapshot on restore."""
    start_cwd = run.get("metadata", {}).get("start_cwd", "")
    skill: str | None = current.get("skill")
    model: str | None = current.get("resolved_model")
    if model is None:
        model = _resolve_skill_model(
            skill,
            start_cwd,
            phase_path=current.get("phase_path"),
            phase_model=current.get("model"),
        )
    instruction = _phase_instruction(
        skill,
        run["issue_id"],
        model,
        harness=_resolve_harness(current, start_cwd),
        run_id=run_id,
        phase_id=current["id"],
        parent_session=discover_agent_session_id(),
        skill_base=Path(start_cwd) / ".claude" / "skills" if start_cwd else None,
    )
    execution = current.get("deterministic_execution")
    if isinstance(execution, dict) and execution.get("status") == "passed":
        instruction = (
            "Deterministic commands executed successfully; call "
            "pipeline_advance to complete the phase."
        )
    result: dict[str, Any] = {"instruction": instruction, "skill": skill}
    result.update(_phase_execution_contract(current, model))
    return result


def _get_phases(run: dict[str, Any]) -> list[dict[str, Any]]:
    """Get all phases from a run."""
    return run["phases"]  # type: ignore[return-value]


@local_only
def pipeline_list(cwd: str = "") -> str:
    """List available pipelines with their phases.

    Args:
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "pipeline_list")
    if isinstance(_root, dict):
        return json.dumps(_root)
    loader = _loader(str(_root) if cwd else cwd)
    pipelines = loader.list_available()
    result: list[dict[str, Any]] = []
    for name in pipelines:
        p = loader.load(name)
        phases = [{"id": ph.id, "skill": ph.skill, "type": ph.type} for ph in p.phases]
        result.append({"name": p.name, "description": p.description, "phases": phases})
    return compact_response(result)


async def _populate_story_stats(project_root: Path, story_id: str) -> None:
    """Fire-and-forget: capture git stats for story_id and write to story_stats."""
    try:
        import subprocess

        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )
        branch = branch_result.stdout.strip()
        if not branch:
            return

        log_result = subprocess.run(
            ["git", "log", "--oneline", branch],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )
        lines = [ln for ln in log_result.stdout.strip().split("\n") if ln]
        commit_count = len(lines)
        last_sha = lines[0].split()[0] if lines else ""
        updated_at = datetime.now(UTC).isoformat()

        pid = get_project_id(project_root)
        conn = get_project_db(project_root)
        create_all(conn)
        try:
            from raise_cli.storage.work_items import WorkItemStore

            work_item_id: str | None = None
            try:
                wi = WorkItemStore(project_root).get_by_jira_key(story_id)
                if wi is not None:
                    work_item_id = wi.id
            except Exception:  # noqa: BLE001
                _log.debug("work_item_id lookup failed for story_stats", exc_info=True)

            conn.execute(
                "INSERT OR REPLACE INTO story_stats"
                "(project_id, story_id, branch, commit_count, last_commit_sha, "
                "work_item_id, updated_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (
                    pid,
                    story_id,
                    branch,
                    commit_count,
                    last_sha,
                    work_item_id,
                    updated_at,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        _log.debug("story_stats populate failed", exc_info=True)


async def _populate_issue_cache(project_root: Path, issue_id: str) -> None:
    """Fire-and-forget: fetch issue summary via backlog adapter and write to issue_cache."""
    try:
        from raise_cli.adapters.resolve import resolve_pm_adapter
        from raise_cli.storage.connection import get_project_db
        from raise_cli.storage.schema import create_all

        adapter = resolve_pm_adapter(None)
        issue = await asyncio.get_running_loop().run_in_executor(
            None, adapter.get_issue, issue_id
        )
        summary: str = issue.summary
        if not summary:
            return
        fetched_at = datetime.now(UTC).isoformat()
        conn = get_project_db(project_root)
        create_all(conn)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO issue_cache"
                "(key, summary, fetched_at) VALUES (?,?,?)",
                (issue_id, summary, fetched_at),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        _log.debug("issue_cache populate failed", exc_info=True)


def _check_maintenance_lock() -> dict[str, Any] | None:
    """Read-only lock check for db_consolidation — fail-open on any error (S8371.3).

    Returns a maintenance status dict when consolidation is actively running,
    or None when the lock is free (or unavailable — fail-open per ADR-104 D3).
    """
    conn = None
    try:
        from raise_cli.storage.connection import get_global_db
        from raise_cli.storage.maintenance_lock import MaintenanceLockStore
        from raise_cli.storage.schema import create_all

        conn = get_global_db()
        create_all(conn)
        store = MaintenanceLockStore(conn)
        lock = store.get("db_consolidation")
        if lock is not None and not store.is_expired_and_dead(lock):
            return {
                "status": "maintenance",
                "reason": "db_consolidation_active",
                "holder_pid": lock.pid,
                "expires_at": lock.expires_at,
                "backoff_hint": "Retry in 30s — consolidation in progress.",
            }
    except Exception:  # noqa: BLE001,S110 — fail-open: never block pipeline on lock check
        pass
    finally:
        if conn is not None:
            conn.close()
    return None


async def _check_issue_type_guard(
    pipeline: PipelineDefinition, issue_id: str
) -> dict[str, Any] | None:
    """Reject when issue_id's actual Jira type isn't in pipeline.issue_types.

    Enforces the invariant declared in each pipeline YAML (bugfix.yaml:
    issue_types: [bug, bugfix], etc. — see PipelineDefinition.issue_types,
    raise_core.workflow.models:202) that was loaded into memory but never
    read (RAISE-13639): a Story routed through the bugfix pipeline was
    admitted silently and only failed 3 phases later, at the triage phase's
    ODC custom-field write, with a message that pointed at the field instead
    of the real cause.

    - Skipped entirely (returns None, no adapter round-trip) when the
      pipeline declares no issue_types.
    - Fail-open on ANY adapter/lookup error (Jira down, unknown key, no
      adapter configured) — mirrors every other guard in this module
      (_check_maintenance_lock, _check_worktree_drift_gate): infra flakiness
      must never block a legit pipeline start.
    - On a genuine mismatch, returns a structured rejection naming both
      remedies: start the pipeline that matches the issue's actual type, or
      retype the issue in Jira to one of the allowed types (the latter also
      makes downstream ODC writes valid for bugfix).
    """
    if not pipeline.issue_types:
        return None
    try:
        from raise_cli.adapters.resolve import resolve_pm_adapter

        adapter = resolve_pm_adapter(None)
        issue = await asyncio.get_running_loop().run_in_executor(
            None, adapter.get_issue, issue_id
        )
        actual_type = (issue.issue_type or "").strip().lower()
        allowed = {t.strip().lower() for t in pipeline.issue_types}
        if actual_type and actual_type not in allowed:
            allowed_display = ", ".join(pipeline.issue_types)
            return {
                "status": "rejected",
                "reason": "issue_type_mismatch",
                "issue_id": issue_id,
                "issue_type": issue.issue_type,
                "pipeline_name": pipeline.name,
                "allowed_types": list(pipeline.issue_types),
                "recovery_hint": (
                    f"{issue_id} is type '{issue.issue_type}', but pipeline "
                    f"'{pipeline.name}' only accepts: {allowed_display}. "
                    f"Start the pipeline that matches '{issue.issue_type}' "
                    f"instead, or retype {issue_id} in Jira to one of the "
                    "allowed types (required for downstream field writes "
                    "that assume that type, e.g. bugfix's ODC fields)."
                ),
            }
    except Exception:  # noqa: BLE001,S110 — fail-open: never block pipeline start on adapter errors
        pass
    return None


_DRIFT_BLOCK_DEFAULT = 50


def _read_drift_threshold(repo: Path) -> int:
    """Read the drift-block threshold from committed config, never from env.

    Source is ``[tool.rai] drift_block_threshold`` in the project's
    ``pyproject.toml``. RAISE-14278: an env var here (``RAISE_DRIFT_BLOCK_THRESHOLD``)
    was an agent-controlled escape hatch — an agent could raise it at runtime
    to defeat its own drift gate. Config committed to the repo is reviewable
    in an MR; an env var set in the agent's own shell is not. Falls back to
    ``_DRIFT_BLOCK_DEFAULT`` when the file, table, or key is absent/invalid —
    never raises, so a missing/malformed pyproject.toml degrades to default
    behavior rather than crashing pipeline_start.
    """
    try:
        data = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return _DRIFT_BLOCK_DEFAULT
    tool = data.get("tool")
    rai = tool.get("rai") if isinstance(tool, dict) else None
    value = rai.get("drift_block_threshold") if isinstance(rai, dict) else None
    return (
        value
        if isinstance(value, int) and not isinstance(value, bool)
        else _DRIFT_BLOCK_DEFAULT
    )


def _check_worktree_drift_gate(cwd: str, repo: Path) -> dict[str, Any] | None:
    """Return rejection dict, warn dict, indeterminate dict, or None (skip/ok).

    - None → no drift info (no target, no cwd, or at-zero-commits) → proceed.
    - {"status": "rejected", ...} → BLOCK pipeline_start.
    - {"drift_warning": {...}} → advisory; run proceeds with warning in payload.
    - {"drift_check": "indeterminate", "warning": {...}} → neither ref resolved;
      fail-loud, NOT fail-closed — run proceeds, response flags indeterminate
      (RAISE-14279). Refs unavailable are legitimate in fresh clones/offline
      work; blocking there would break sane local work. The fail-closed point
      lives in CI, where refs are guaranteed.

    Prefers origin/{merge_target} for the count; falls back to the local ref
    ONLY when the first is indeterminate (None) — an actually-evaluated 0 is
    no drift and needs no fallback.
    """
    if not cwd:
        return None
    merge_target = get_worktree_merge_target(repo, Path(cwd))
    if not merge_target:
        return None
    # Count drift from the calling worktree's CWD, not the resolved project
    # root: in a worktree the project root resolves to the main repo, whose
    # HEAD belongs to an unrelated session and yields a bogus count (RAISE-9192).
    worktree = Path(cwd)
    target_ref = f"origin/{merge_target}"
    behind = commits_behind(worktree, target_ref)
    if behind is None:
        target_ref = merge_target
        behind = commits_behind(worktree, target_ref)
    if behind is None:
        _log.warning(
            "drift check indeterminate for %s: neither origin/%s nor %s resolved",
            worktree,
            merge_target,
            merge_target,
        )
        return {
            "drift_check": "indeterminate",
            "warning": {
                "reason": "refs_unavailable",
                "merge_target": merge_target,
                "hint": (
                    f"No se pudo evaluar drift contra '{merge_target}' "
                    "(ref no encontrada/git no disponible). Ejecuta: "
                    "git fetch origin"
                ),
            },
        }
    if behind == 0:
        return None
    threshold = _read_drift_threshold(repo)
    hint = (
        f"El worktree está {behind} commits detrás de {target_ref}. "
        f"Ejecuta: git merge {target_ref}"
    )
    if behind > threshold:
        return {
            "status": "rejected",
            "reason": "drift_behind",
            "commits_behind": behind,
            "merge_target": merge_target,
            "recovery_hint": hint,
        }
    return {
        "drift_warning": {
            "commits_behind": behind,
            "merge_target": merge_target,
            "hint": hint,
        }
    }


def _serialize_phase(
    ph: Any,
    *,
    phase_path: str | None = None,
    cwd: str = "",
) -> dict[str, Any]:
    """Serialize a PhaseDefinition to a plain dict for run state storage (D1, RAISE-15030)."""
    declared_model: str | None = getattr(ph, "model", None)
    resolved_model = _resolve_skill_model(
        getattr(ph, "skill", None),
        cwd,
        phase_path=phase_path,
        phase_model=declared_model,
    )
    return {
        "id": ph.id,
        "skill": ph.skill,
        "type": ph.type,
        "commands": list(getattr(ph, "commands", [])),
        "model": declared_model,
        "max_budget_usd": getattr(ph, "max_budget_usd", 5.0),
        "phase_path": phase_path,
        "resolved_model": resolved_model,
        "gate_type": ph.gate.type if ph.gate else None,
        "gate_impact": ph.gate.impact if ph.gate else None,
        "validates": [
            (
                {"store": v.store, "type": v.type, "description": v.description}
                if v.store
                else {
                    "patterns": list(v.patterns),
                    "description": v.description,
                }
                if v.patterns
                else {"pattern": v.pattern, "description": v.description}
            )
            for v in ph.validates
        ],
        "when": ph.when,
        "workflow_point": ph.workflow_point,
        "status": "pending",
        "context_spec": (
            [{"types": g.types, "limit": g.limit} for g in ph.context.graph]
            if ph.context
            else None
        ),
        "review_mode": ph.review_mode,
        "review_template": ph.review_template,
        "quality_gates": ph.quality_gates,
        "gate_mode": ph.gate_mode,
        "pipeline": ph.pipeline,
        "foreach": ph.foreach,
        "success_policy": ph.success_policy,
        "target_status": ph.target_status,
        "transition_mode": ph.transition_mode,
        "harness": getattr(ph, "harness", None),
    }


async def _execute_mcp_deterministic_phase(
    phase: dict[str, Any],
    cwd: str,
    *,
    checkpoint: Callable[[], Awaitable[None]] | None = None,
) -> dict[str, Any] | None:
    """Execute one snapshotted deterministic phase at most once.

    Pipeline YAML is trusted repository configuration.  The execution record is
    stored on the phase before the run is returned to the orchestrator, so a
    duplicate start or advance observes the prior result instead of replaying
    commands.
    """
    if phase.get("type") != "deterministic":
        return None

    existing = phase.get("deterministic_execution")
    if isinstance(existing, dict):
        return existing

    commands = [str(command) for command in phase.get("commands", [])]
    record: dict[str, Any] = {
        "status": "running",
        "commands": commands,
        "started_at": datetime.now(UTC).isoformat(),
        "results": [],
    }
    phase["deterministic_execution"] = record
    if checkpoint is not None:
        # Persist intent before launching any external side effect.  If this
        # process dies after the checkpoint, a resumed caller sees ``running``
        # and fails closed instead of replaying an uncertain command.
        await checkpoint()

    for command in commands:
        try:
            argv = shlex.split(command)
            exe = shutil.which(argv[0]) if argv else None
            if exe is not None:
                argv[0] = exe
            elif argv and argv[0] == "rai":
                argv = [*get_rai_executable(), *argv[1:]]
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=cwd or None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            record["results"].append(
                {
                    "command": command,
                    "returncode": None,
                    "error": f"spawn_error: {exc}",
                }
            )
            record["status"] = "failed"
            break
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300.0)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            record["results"].append(
                {"command": command, "returncode": None, "error": "timeout"}
            )
            record["status"] = "failed"
            break

        result = {
            "command": command,
            "returncode": proc.returncode,
            "stdout": stdout.decode(errors="replace")[-8000:],
            "stderr": stderr.decode(errors="replace")[-8000:],
        }
        record["results"].append(result)
        if proc.returncode != 0:
            record["status"] = "failed"
            break
    else:
        record["status"] = "passed"

    record["completed_at"] = datetime.now(UTC).isoformat()
    return record


async def _checkpoint_run(store: Any, run: dict[str, Any]) -> None:
    """Persist an execution intent and refresh its optimistic-lock version."""
    await store.save(run)
    refreshed = await store.load(run["run_id"])
    if refreshed is not None and "version" in refreshed:
        run["version"] = refreshed["version"]


async def _release_preflight_at_start(
    project: Path, issue_id: str
) -> ReleasePreflightResult:
    """Run release preflight without blocking the async MCP event loop."""
    from raise_cli.adapters.protocols import ProjectVersionManagementAdapter
    from raise_cli.adapters.resolve import resolve_pm_adapter
    from raise_cli.project_config import resolve_dev_branch
    from raise_cli.release_preflight import run_release_preflight

    development_branch = resolve_dev_branch(project)
    project_key = issue_id.split("-", 1)[0] if "-" in issue_id else ""

    def run() -> ReleasePreflightResult:
        adapter = None
        adapter_error = ""
        try:
            candidate = resolve_pm_adapter(None, project_root=project)
            if isinstance(candidate, ProjectVersionManagementAdapter):
                adapter = candidate
            else:
                adapter_error = "configured adapter cannot list project versions"
        except Exception as exc:  # noqa: BLE001 — start preflight is advisory
            adapter_error = str(exc)
        return run_release_preflight(
            project,
            development_branch,
            project_key=project_key,
            adapter=adapter,
            adapter_error=adapter_error,
        )

    return await asyncio.to_thread(run)


@local_only
async def pipeline_start(  # noqa: C901 — multiple early-return guards (lease, drift, dedup, store); splitting breaks single-invocation contract
    pipeline_name: str, issue_id: str, cwd: str = "", size: str = ""
) -> str:
    """Start a pipeline run. Returns the first phase to execute.

    Args:
        pipeline_name: Pipeline name (e.g., 'story', 'epic', 'bugfix')
        issue_id: Issue key for traceability (e.g., 'RAISE-1281')
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2); also enables lease enforcement (ADR-094).
            Inert under HTTP transport / server credentials.
        size: Optional work size (XS|S|M|L) for the proportionality aspect
            (ADR-116). Recorded in run metadata; gates size-conditional phases.
            Unset → fail-safe full ceremony.
    """
    from raise_cli.pipeline.lease_enforcement import enforce
    from raise_cli.project import resolve_project_root

    caller_root = _caller_context.require_caller_cwd(cwd, "pipeline_start")
    if isinstance(caller_root, dict):
        return json.dumps(caller_root)

    identity_mismatch = _check_mcp_worktree_identity(cwd)
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    decision = enforce(cwd)
    if decision.status == "rejected":
        return json.dumps(decision.to_payload())

    _repo = resolve_project_root(caller_root)
    drift_gate = _check_worktree_drift_gate(cwd, _repo)
    if drift_gate and "status" in drift_gate:
        return json.dumps(drift_gate)

    maintenance = _check_maintenance_lock()
    if maintenance:
        return json.dumps(maintenance)

    store = get_run_store()
    loader = _loader(cwd)
    try:
        pipeline = loader.load(pipeline_name)
    except PipelineError:
        return json.dumps(
            {"status": "error", "reason": f"Pipeline not found: {pipeline_name}"}
        )

    # T4 (RAISE-14938): fail-closed quality_gates ID validation — unknown gate
    # IDs are rejected upfront so no phase executes with a bad gate ID.
    try:
        from raise_cli.gates.execution import validate_quality_gate_ids

        validate_quality_gate_ids(pipeline.phases)
    except PipelineError as exc:
        return json.dumps({"status": "error", "reason": str(exc)})

    type_guard = await _check_issue_type_guard(pipeline, issue_id)
    if type_guard:
        return json.dumps(type_guard)

    # Dedup: one orchestrator per (issue, pipeline) — a second start gets
    # the existing run instead of forking a parallel orchestration (S8170.4).
    existing_runs = await store.list_runs()
    for existing in existing_runs:
        if (
            existing.get("issue_id") == issue_id
            and existing.get("pipeline_name") == pipeline_name
            and existing.get("status") in ("started", "running", "paused")
        ):
            existing_phases = existing.get("phases") or []
            idx = existing.get("current_phase_index", 0)
            phase_id = existing_phases[idx]["id"] if idx < len(existing_phases) else "?"
            is_foreign, owner_desc = is_foreign_live_run(existing)
            if is_foreign:
                hint = (
                    f"Run {pipeline_name} activo para {issue_id} en fase "
                    f"{phase_id} pertenece a {owner_desc}. "
                    f"NO canceles — es trabajo en vuelo de otra sesión. "
                    f"Retómalo con pipeline_advance(run_id="
                    f"{existing['run_id']}) solo si sabes que la sesión "
                    f"propietaria ya no existe."
                )
            else:
                hint = (
                    f"Ya existe un run {pipeline_name} activo para "
                    f"{issue_id} en fase {phase_id}. Retómalo con "
                    f"pipeline_status/pipeline_advance(run_id="
                    f"{existing['run_id']}) o cancélalo con "
                    "pipeline_cancel."
                )
            return json.dumps(
                {
                    "status": "rejected",
                    "reason": "duplicate_run",
                    "existing_run_id": existing["run_id"],
                    "current_phase": phase_id,
                    "recovery_hint": hint,
                }
            )

    # Best-effort orphan lock reap (RAISE-11089). Deliberately placed AFTER
    # the dedup early-return above (ar.md R1) — a session resuming its own
    # matching (issue, pipeline) run returns early above and never reaches
    # this call, so reaping only ever runs when we're actually about to
    # lock a NEW run onto this worktree, never on a resume path. Reuses
    # existing_runs (already fetched for dedup) — no extra store round-trip.
    from raise_cli.pipeline.worktree_lock import reap_orphan_worktree_locks

    reap_orphan_worktree_locks(
        cwd, existing_runs, lease_is_dead=decision.prior_holder_dead
    )

    # Full UUID string — PostgresRunStore requires a valid UUID (the row PK
    # is `uuid` typed). Truncated 8-char prefix worked for JSON files but
    # breaks the DB backend.
    run_id = str(uuid4())
    phases: list[dict[str, Any]] = [
        _serialize_phase(
            ph,
            phase_path=f"{pipeline_name}.{ph.id}",
            cwd=cwd,
        )
        for ph in pipeline.phases
    ]

    run: dict[str, Any] = {
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "issue_id": issue_id,
        "current_phase_index": 0,
        "phases": phases,
        "started_at": datetime.now(UTC).isoformat(),
        "metadata": {},
    }

    # Store start_cwd so pipeline_advance can resolve globs against the correct
    # worktree even when the caller omits cwd on subsequent calls (RAISE-8470).
    if cwd:
        run["metadata"]["start_cwd"] = cwd

    # RAISE-12207/15387: capture the agent session id ONCE at start (the earliest
    # agent-initiated call) so the engine's `before:bug:close` emit can re-check
    # the session-scoped AR marker under the SAME identity the review skill uses.
    # Runtimes without an exported session id get a stable run-scoped identity;
    # phase prompts carry it explicitly, so close never falls back to ambiguous
    # MCP-server environment discovery.
    _start_session_id = discover_agent_session_id() or f"pipeline-{run_id}"
    run["metadata"]["agent_session_id"] = _start_session_id

    # RAISE-13580: mint a per-run advance capability token. A resumed
    # Task/Agent subagent shares session_id/PID/MCP connection with the
    # orchestrator, so no ambient signal distinguishes them — possession of
    # this secret (returned to the caller ONCE, below) is the irreducible
    # discriminator. Only the SHA-256 hash is persisted; the plaintext never
    # touches storage. `metadata` is schemaless JSON → zero DDL.
    _advance_token = secrets.token_urlsafe(16)
    run["metadata"]["advance_token_hash"] = hashlib.sha256(
        _advance_token.encode()
    ).hexdigest()

    # Proportionality aspect (ADR-116): record work size so the advance loop can
    # skip size-gated phases. Unset → fail-safe full ceremony (engine treats
    # missing size as the largest tier).
    if size:
        run["metadata"]["size"] = size.strip().upper()

    # Best-effort cleanup protection while the pipeline is active (S8170.6).
    from raise_cli.pipeline.worktree_lock import lock_worktree

    locked_path = lock_worktree(cwd, run_id)
    if locked_path:
        run["metadata"]["locked_worktree"] = locked_path

    release_preflight = None
    if cwd:
        release_preflight = await _release_preflight_at_start(Path(cwd), issue_id)
        run["metadata"]["release_preflight"] = release_preflight.model_dump(mode="json")

    # Track phase start time for duration calculation
    phases[0]["started_at"] = datetime.now(UTC).isoformat()

    deterministic_result = await _execute_mcp_deterministic_phase(
        phases[0],
        cwd,
        checkpoint=lambda: _checkpoint_run(store, run),
    )
    if deterministic_result and deterministic_result.get("status") == "failed":
        run["status"] = "failed"
        await store.save(run)
        from raise_cli.pipeline.worktree_lock import unlock_worktree

        unlock_worktree(run.get("metadata", {}).get("locked_worktree"))
        return json.dumps(
            {
                "status": "deterministic_failed",
                "run_id": run_id,
                "current_phase": phases[0]["id"],
                "execution": deterministic_result,
            }
        )

    await store.save(run)
    _task = asyncio.create_task(
        _populate_issue_cache(resolve_project_root(caller_root), issue_id)
    )
    _BACKGROUND_TASKS.add(_task)
    _task.add_done_callback(_BACKGROUND_TASKS.discard)

    first = phases[0]
    skill: str | None = first.get("skill")
    context_skill = skill or ""
    skill_model: str | None = first.get("resolved_model")
    instruction = _phase_instruction(
        skill,
        issue_id,
        skill_model,
        harness=_resolve_harness(first, cwd),
        run_id=run_id,
        phase_id=first["id"],
        parent_session=_start_session_id,
        skill_base=Path(cwd) / ".claude" / "skills" if cwd else None,
    )
    if deterministic_result is not None:
        instruction = (
            "Deterministic commands executed successfully; call "
            "pipeline_advance to complete the phase."
        )
    start_result: dict[str, Any] = {
        "run_id": run_id,
        "status": "running",
        "total_phases": len(phases),
        "current_phase": first["id"],
        # RAISE-13580: returned exactly once. The orchestrator must present it
        # on every pipeline_advance. Do NOT include it in subagent briefs — a
        # resumed subagent that receives it inherits the ability to drive this
        # run's queue, which is the exact bug this token closes.
        "advance_token": _advance_token,
        "advance_token_warning": (
            "Secret authorizing pipeline_advance for this run only. Keep it in "
            "the orchestrator; do NOT include advance_token in subagent briefs."
        ),
        "instruction": instruction,
        "skill": skill,
        "gate": first["gate_type"],
        "context": _build_phase_context(
            first["id"],
            context_skill,
            run,
            context_spec=first.get("context_spec"),
            search_root=Path(cwd) if cwd else None,
        ),
    }
    start_result.update(_phase_execution_contract(first, skill_model))
    start_result["rai_meta"] = {
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "agent_session_id": _start_session_id,
    }
    if first.get("review_mode"):
        start_result["review_mode"] = first["review_mode"]
        start_result["review_template"] = first.get("review_template")
    if decision.warning:
        start_result["warning"] = decision.warning
    if drift_gate and "drift_warning" in drift_gate:
        start_result["drift_warning"] = drift_gate["drift_warning"]
    if drift_gate and "drift_check" in drift_gate:
        start_result["drift_check"] = drift_gate["drift_check"]
        start_result["drift_check_warning"] = drift_gate["warning"]
    if release_preflight is not None:
        start_result["release_preflight"] = release_preflight.model_dump(mode="json")
    return json.dumps(start_result)


_MAX_WRITE_RETRIES = 3

# RAISE-15048 (Sol W4): version stamp for the new pipeline_runs.metadata keys
# (hitl_decisions, awaiting_gate). Writers stamp `_v`; readers (P2 cockpit)
# treat metadata.get("_v", 0) < 1 as legacy — no new-key contract to honor.
METADATA_VERSION = 1

# RAISE-15048: decision journal is capped so a runaway loop of pipeline_decision
# calls can't grow run metadata unbounded (Sol S5 — no control effect, but
# still bounded storage).
_MAX_HITL_DECISIONS = 50


def _append_hitl_decision(
    run: dict[str, Any], decision: str, phase: str, *, source: str
) -> None:
    """Append an entry to the run's decision journal (metadata.hitl_decisions).

    Display-only governance trail (design §2) — no control effect on the
    pipeline. Capped at `_MAX_HITL_DECISIONS` (oldest dropped first) and
    truncated at 2000 chars per entry.
    """
    metadata = run.setdefault("metadata", {})
    journal: list[dict[str, Any]] = metadata.setdefault("hitl_decisions", [])
    journal.append(
        {
            "decision": decision[:2000],
            "phase": phase,
            "source": source,
            "at": datetime.now(UTC).isoformat(),
        }
    )
    if len(journal) > _MAX_HITL_DECISIONS:
        del journal[: len(journal) - _MAX_HITL_DECISIONS]
    metadata["_v"] = METADATA_VERSION


def _emit_mcp_hitl_decision(
    run: dict[str, Any],
    *,
    phase_id: str,
    decision: str,
    actor_kind: str,
    detail: str | None = None,
) -> None:
    """Emit a governance audit ``hitl_decision`` from an MCP resolution site (SD3c).

    Covers ``_advance_once`` (approve/auto-approved, next to
    ``_append_hitl_decision``) and ``_decide_once`` (journal-only directional
    decisions — free text, normalized inside ``emit_hitl_decision``).
    Fail-open: wrapped so a raising emitter can never affect the run mutation
    or response already computed by the caller.
    """
    try:
        emit_hitl_decision(
            phase_id=phase_id,
            decision=decision,
            actor_kind=actor_kind,  # type: ignore[arg-type]
            work_item_ref=run.get("issue_id"),
            run_id=run.get("run_id"),
            pipeline_name=run.get("pipeline_name"),
            branch=run.get("branch"),
            commit=run.get("final_commit"),
            detail=detail,
            session_id=run.get("metadata", {}).get("agent_session_id"),
        )
    except Exception:  # noqa: BLE001 — fail-open by design (SD3)
        _log.debug("governance audit emission failed (hitl_decision)", exc_info=True)


def _stamp_awaiting_gate(run: dict[str, Any], phase_id: str) -> None:
    """Set/refresh the awaiting_gate stamp on metadata (design §1, Sol S7/R4).

    `entered_at` is set once when the phase first blocks on its gate and stays
    immutable across repeated gate_pending checks for the SAME phase;
    `last_checked_at` refreshes on every check. A phase change resets both —
    this is a new gate wait, not a continuation of the old one.
    """
    metadata = run.setdefault("metadata", {})
    existing: dict[str, Any] | None = metadata.get("awaiting_gate")
    now = datetime.now(UTC).isoformat()
    if existing and existing.get("phase") == phase_id:
        existing["last_checked_at"] = now
    else:
        metadata["awaiting_gate"] = {
            "phase": phase_id,
            "entered_at": now,
            "last_checked_at": now,
        }
    metadata["_v"] = METADATA_VERSION


def _verify_run_authority(
    run: dict[str, Any], advance_token: str
) -> dict[str, Any] | None:
    """Gate advance authority on possession of the per-run token (RAISE-13580).

    Returns a structured AUTHORITY_DENIED refusal (no state mutation) when a
    token-bearing run is advanced without the matching secret; returns None
    (proceed) on a valid token OR on a legacy run that predates the feature
    (null hash → fail-open advisory, zero-migration rollout).

    Comparison is constant-time (`hmac.compare_digest`) to avoid leaking the
    stored hash byte-by-byte via timing.
    """
    stored: str | None = run.get("metadata", {}).get("advance_token_hash")
    if not stored:
        # Legacy run minted before the token feature — proceed with advisory.
        return None

    provided = hashlib.sha256(advance_token.encode()).hexdigest()
    if hmac.compare_digest(provided, stored):
        return None

    return {
        "status": "authority_denied",
        "reason": (
            "AUTHORITY_DENIED: this run requires the advance_token issued once "
            "by pipeline_start. A resumed subagent does not hold it. If the "
            "orchestrator lost the token (compaction/crash), call "
            "`pipeline_restore(run_id, cwd=...)` — it auto-reissues a new "
            "token when the worktree lease is acquired."
        ),
    }


def _evaluate_guardrails(
    cwd: str, *, started_at: datetime | None = None
) -> dict[str, Any] | None:
    """Evaluate loop detection + circuit breaker for the current session.

    Returns a guardrails dict if any signal fires, None when clean or on error.
    Always fail-open: any exception returns None (S8741.3).

    Args:
        cwd: Working directory for DB and JSONL resolution.
        started_at: Phase start timestamp. When provided, scan_single_session
            is bounded to events at or after this time so only phase-level
            metrics feed the evaluator (RAISE-9839).
    """
    try:
        from raise_cli.storage.connection import get_project_db_path
        from raise_cli.telemetry.cost_report import scan_single_session
        from raise_cli.telemetry.guardrails import (
            check_circuit_breaker,
            check_loop_patterns,
            rolling_avg_from_sqlite,
        )
        from raise_cli.telemetry.session_tokens import find_current_session_jsonl

        working_dir = Path(cwd) if cwd else Path.cwd()
        db_path = get_project_db_path(working_dir)
        rolling_avg = rolling_avg_from_sqlite(db_path)

        jsonl = find_current_session_jsonl(working_dir)
        if jsonl is None:
            return None

        report = scan_single_session(jsonl, since=started_at)
        loop_result = check_loop_patterns(report)
        cb_result = check_circuit_breaker(report, rolling_avg)

        if not loop_result.triggered and not cb_result.triggered:
            return None

        severity = (
            "block"
            if (loop_result.severity == "block" or cb_result.severity == "block")
            else "warn"
        )
        patterns: list[str] = list(loop_result.patterns_active)

        guardrails: dict[str, Any] = {
            "triggered": True,
            "severity": severity,
            "patterns_active": patterns,
        }
        if loop_result.triggered and loop_result.reason:
            guardrails["loop_reason"] = loop_result.reason
        if cb_result.triggered and cb_result.reason:
            guardrails["circuit_breaker_reason"] = cb_result.reason
        # RAISE-9839: without a phase start boundary the scan covers the full
        # session, so session-accumulated failures can inflate severity. Cap
        # at "warn" to prevent false block verdicts; mark for observability.
        if started_at is None and severity == "block":
            severity = "warn"
            guardrails["severity"] = severity
            guardrails["boundary_fallback"] = True
        return guardrails
    except Exception:  # noqa: BLE001
        _log.debug("Guardrails evaluation failed — fail-open", exc_info=True)
        return None


@local_only
async def pipeline_advance(
    run_id: str,
    approve: bool = False,
    cwd: str = "",
    advance_token: str = "",
    phase: str = "",
) -> str:
    """Mark current phase as done and get the next phase.

    Call this after completing the skill for the current phase.
    If the current phase has an HITL gate, returns gate_pending.
    Call again with approve=True to pass the gate.

    Args:
        run_id: The run ID returned by pipeline_start.
        approve: Set to True to approve an HITL gate on the current phase.
        cwd: Working directory for artifact resolution. Required when calling
            from a git worktree (the MCP server CWD differs from the session's).
            Defaults to the server's CWD when empty.
        advance_token: The per-run capability token returned once by
            pipeline_start. Required for token-bearing runs (RAISE-13580);
            a resumed subagent that never received it is refused with
            AUTHORITY_DENIED before any lease renewal or state mutation.
        phase: Expected phase id (D5, RAISE-15030). When provided, the advance
            is rejected with status "phase_mismatch" if the run's current phase
            differs — prevents retry-after-write-race from transitioning the
            wrong phase.
    """
    identity_mismatch = _check_mcp_worktree_identity(cwd)  # S15457.4
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    # Losers of a write race reload fresh state and retry with backoff —
    # _advance_once starts from store.load, so each attempt re-evaluates
    # rather than re-applying a stale mutation (S8170.5, research F8).
    for attempt in range(_MAX_WRITE_RETRIES):
        try:
            return await _advance_once(
                run_id,
                approve=approve,
                cwd=cwd,
                advance_token=advance_token,
                expected_phase=phase,
            )
        except OptimisticLockError:
            if attempt < _MAX_WRITE_RETRIES - 1:
                await asyncio.sleep(0.05 * 2**attempt)
    return json.dumps(
        {
            "status": "error",
            "reason": (
                f"write_conflict_exhausted: run {run_id} lost "
                f"{_MAX_WRITE_RETRIES} consecutive write races — another "
                "session may be advancing this run; retry or check leases"
            ),
        }
    )


async def _decide_once(run_id: str, decision: str, phase: str) -> str:
    """Single-attempt body for pipeline_decision.

    Retried by the wrapper on OptimisticLockError (mirrors
    _advance_once/pipeline_advance).
    """
    store = get_run_store()
    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    idx: int = run.get("current_phase_index", 0)
    phases = _get_phases(run)
    current_phase_id = phases[idx]["id"] if idx < len(phases) else ""
    resolved_phase = phase or current_phase_id

    _append_hitl_decision(run, decision, resolved_phase, source="agent")
    _emit_mcp_hitl_decision(
        run,
        phase_id=resolved_phase,
        decision=decision,
        actor_kind="agent",
        detail=decision,
    )
    await store.save(run)

    return json.dumps(
        {
            "status": "ok",
            "run_id": run_id,
            "phase": resolved_phase,
            "decisions_count": len(run["metadata"]["hitl_decisions"]),
        }
    )


@local_only
async def pipeline_decision(
    run_id: str, decision: str, phase: str = "", cwd: str = ""
) -> str:
    """Persist a directional human decision into the run's journal.

    Display-only governance trail (RAISE-15048 / design §2.2) — appends to
    metadata.hitl_decisions with source="agent". Has NO control effect: it
    cannot advance, pause, or cancel the run. Deliberately does not require
    advance_token — requiring it here would force the capability token into
    subagent reach, the exact thing RAISE-13580 forbids.

    Args:
        run_id: The run ID returned by pipeline_start.
        decision: Free-text summary of the directional decision (truncated
            at 2000 chars).
        phase: Phase id to attribute the decision to. Defaults to the run's
            current phase when omitted.
        cwd: Caller's checkout path. When provided with a server-asserted root
            (RAISE_PROJECT_ROOT / --project), the caller root must match or the
            request is rejected with worktree_mismatch (S15457.4).
    """
    identity_mismatch = _check_mcp_worktree_identity(cwd)  # S15457.4
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    for attempt in range(_MAX_WRITE_RETRIES):
        try:
            return await _decide_once(run_id, decision, phase)
        except OptimisticLockError:
            if attempt < _MAX_WRITE_RETRIES - 1:
                await asyncio.sleep(0.05 * 2**attempt)
    return json.dumps(
        {
            "status": "error",
            "reason": (
                f"write_conflict_exhausted: run {run_id} lost "
                f"{_MAX_WRITE_RETRIES} consecutive write races — another "
                "session may be writing to this run; retry"
            ),
        }
    )


async def _find_child_run(
    store: Any,
    parent_run_id: str,
    parent_phase: str,
    fanout_key: str | None = None,
) -> dict[str, Any] | None:
    """Find a child run linked to a parent run+phase via metadata."""
    all_runs = await store.list_runs()
    for r in all_runs:
        meta = r.get("metadata", {})
        if (
            meta.get("parent_run_id") == parent_run_id
            and meta.get("parent_phase") == parent_phase
            and (fanout_key is None or meta.get("fanout_key") == fanout_key)
        ):
            return r
    return None


async def _create_child_run(
    parent_run: dict[str, Any],
    child_pipeline_name: str,
    parent_phase_id: str,
    store: Any,
    cwd: str,
    fanout_key: str | None = None,
) -> dict[str, Any]:
    """Create a child PipelineRun linked to a parent via metadata."""
    loader = _loader(cwd)
    child_pipeline = loader.load(child_pipeline_name)

    child_run_id = str(uuid4())
    parent_phase = next(
        (
            phase
            for phase in parent_run.get("phases", [])
            if phase["id"] == parent_phase_id
        ),
        {},
    )
    parent_phase_path = parent_phase.get("phase_path") or (
        f"{parent_run.get('pipeline_name', '')}.{parent_phase_id}"
    )
    child_phases: list[dict[str, Any]] = [
        _serialize_phase(
            ph,
            phase_path=f"{parent_phase_path}.{ph.id}",
            cwd=cwd,
        )
        for ph in child_pipeline.phases
    ]

    _advance_token = secrets.token_urlsafe(16)
    child_run: dict[str, Any] = {
        "run_id": child_run_id,
        "pipeline_name": child_pipeline_name,
        "issue_id": fanout_key if fanout_key else parent_run.get("issue_id", ""),
        "current_phase_index": 0,
        "phases": child_phases,
        "started_at": datetime.now(UTC).isoformat(),
        "status": "running",
        "metadata": {
            "parent_run_id": parent_run["run_id"],
            "parent_phase": parent_phase_id,
            "phase_path_prefix": parent_phase_path,
            "advance_token_hash": hashlib.sha256(_advance_token.encode()).hexdigest(),
        },
    }
    if fanout_key is not None:
        child_run["metadata"]["fanout_key"] = fanout_key
    if cwd:
        child_run["metadata"]["start_cwd"] = cwd

    child_phases[0]["started_at"] = datetime.now(UTC).isoformat()
    deterministic_result = await _execute_mcp_deterministic_phase(
        child_phases[0],
        cwd,
        checkpoint=lambda: _checkpoint_run(store, child_run),
    )
    if deterministic_result and deterministic_result.get("status") == "failed":
        child_phases[0]["status"] = "failed"
        child_run["status"] = "failed"
    await store.save(child_run)

    if child_run.get("status") == "failed":
        return {
            "status": "child_failed",
            "child_run_id": child_run_id,
            "child_pipeline": child_pipeline_name,
            "child_phase": child_phases[0]["id"],
            "execution": deterministic_result,
            "run_id": parent_run["run_id"],
        }

    first_phase = child_phases[0]
    first_skill: str | None = first_phase.get("skill")
    first_model: str | None = first_phase.get("resolved_model")
    first_instruction = _phase_instruction(
        first_skill,
        child_run["issue_id"],
        first_model,
        harness=_resolve_harness(first_phase, cwd),
        run_id=child_run_id,
        phase_id=first_phase["id"],
        parent_session=discover_agent_session_id(),
        skill_base=Path(cwd) / ".claude" / "skills" if cwd else None,
    )
    if deterministic_result is not None:
        first_instruction = (
            "Deterministic commands executed successfully; call "
            "pipeline_advance to complete the phase."
        )
    result: dict[str, Any] = {
        "status": "delegated",
        "child_run_id": child_run_id,
        "child_pipeline": child_pipeline_name,
        "child_phase": first_phase["id"],
        "advance_token": _advance_token,
        "run_id": parent_run["run_id"],
        "instruction": first_instruction,
        "skill": first_skill,
    }
    result.update(_phase_execution_contract(first_phase, first_model))
    return result


async def _dispatch_composite(
    run: dict[str, Any],
    current_phase: dict[str, Any],
    child_pipeline_name: str,
    store: Any,
    cwd: str,
) -> dict[str, Any] | None:
    """Handle composite phase dispatch.

    Returns a response dict, or None to fall through to normal phase
    completion (when child is complete).
    """
    foreach_mode = current_phase.get("foreach")
    if foreach_mode == "stories":
        return await _dispatch_foreach(
            run, current_phase, child_pipeline_name, store, cwd
        )
    return await _dispatch_single_child(
        run, current_phase, child_pipeline_name, store, cwd
    )


async def _remint_unused_child_token(child: dict[str, Any], store: Any) -> str | None:
    """Re-mint a child run's advance token when no phase has completed (RAISE-15737).

    The delegation token is show-once: it only travels in the FIRST
    ``delegated`` response. When that response is lost (MCP client timeout),
    the child wedges — only the token's SHA-256 is persisted, so the original
    plaintext is unrecoverable and must be re-minted.

    Heuristic, not proof: "still on phase 0 with no completed phase" CANNOT
    distinguish "token lost" from "token alive mid-phase" — the
    ``gate_pending``, ``artifact_missing`` and ``deterministic_not_executed``
    paths all return after token verification but before phase completion.
    A child parked at a phase-0 HITL gate with a live token WILL have that
    token invalidated by this re-mint (known, accepted tradeoff; recovery for
    that holder is the new token in the same ``delegated`` response, or
    ``rai pipeline token reissue``). The caller reaching this point already
    proved authority over the subtree (the parent's advance_token is verified
    in ``_advance_once`` before dispatch).

    One-shot: the first re-mint stamps ``metadata.reminted_at`` and later
    retries never rotate again — an unbounded per-poll rotation would
    invalidate a live holder on every parent retry. If the re-minted token's
    response is also lost, the documented recovery is
    ``rai pipeline token reissue`` (viable on the main checkout since
    RAISE-15737 Fix B).

    Returns the new plaintext, or None when no re-mint applies (child already
    completed a phase, legacy child without a token hash, or already
    re-minted once).
    """
    if int(child.get("current_phase_index", 0)) != 0:
        return None
    if any(p.get("status") == "completed" for p in child.get("phases", [])):
        return None
    meta = child.get("metadata", {})
    if not meta.get("advance_token_hash"):
        return None
    if meta.get("reminted_at"):
        return None
    token = secrets.token_urlsafe(16)
    meta["advance_token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    meta["reminted_at"] = datetime.now(UTC).isoformat()
    await store.save(child)
    return token


async def _dispatch_single_child(
    run: dict[str, Any],
    current_phase: dict[str, Any],
    child_pipeline_name: str,
    store: Any,
    cwd: str,
) -> dict[str, Any] | None:
    """Sequential sub-pipeline: single child linked to parent phase."""
    parent_run_id = run["run_id"]
    phase_id = current_phase["id"]

    child = await _find_child_run(store, parent_run_id, phase_id)
    if child is None:
        return await _create_child_run(run, child_pipeline_name, phase_id, store, cwd)

    child_status = child.get("status", "")

    if child_status in ("started", "running", "paused"):
        child_idx = child.get("current_phase_index", 0)
        child_phases = child.get("phases", [])
        child_phase = child_phases[child_idx]
        child_skill: str | None = child_phase.get("skill")
        child_model: str | None = child_phase.get("resolved_model")
        child_instruction = _phase_instruction(
            child_skill,
            child.get("issue_id", ""),
            child_model,
            harness=_resolve_harness(child_phase, cwd),
            run_id=child["run_id"],
            phase_id=child_phase["id"],
            parent_session=discover_agent_session_id(),
            skill_base=Path(cwd) / ".claude" / "skills" if cwd else None,
        )
        execution = child_phase.get("deterministic_execution")
        if isinstance(execution, dict) and execution.get("status") == "passed":
            child_instruction = (
                "Deterministic commands executed successfully; call "
                "pipeline_advance to complete the phase."
            )
        result: dict[str, Any] = {
            "status": "delegated",
            "child_run_id": child["run_id"],
            "child_pipeline": child.get("pipeline_name", ""),
            "child_phase": child_phase["id"],
            "run_id": parent_run_id,
            "instruction": child_instruction,
            "skill": child_skill,
        }
        result.update(_phase_execution_contract(child_phase, child_model))
        reminted = await _remint_unused_child_token(child, store)
        if reminted is not None:
            result["advance_token"] = reminted
            result["advance_token_reminted"] = True
        return result

    if child_status in ("failed", "cancelled"):
        return {
            "status": "child_failed",
            "child_run_id": child["run_id"],
            "child_pipeline": child.get("pipeline_name", ""),
            "message": (
                f"Child pipeline '{child.get('pipeline_name', '')}' {child_status} — "
                f"parent phase '{phase_id}' cannot advance."
            ),
            "run_id": parent_run_id,
        }

    # child_status == "complete" → store manifest and fall through
    _store_child_manifest(run, child)
    return None


def _store_child_manifest(
    parent_run: dict[str, Any], child_run: dict[str, Any]
) -> None:
    """Record a child's completion summary in parent metadata."""
    manifests: dict[str, Any] = parent_run.setdefault("metadata", {}).setdefault(
        "child_manifests", {}
    )
    manifests[child_run["run_id"]] = {
        "pipeline_name": child_run.get("pipeline_name", ""),
        "issue_id": child_run.get("issue_id", ""),
        "status": child_run.get("status", ""),
        "completed_at": child_run.get("completed_at", ""),
        "phase_count": len(child_run.get("phases", [])),
    }


async def _pending_child_entries(
    pending: list[dict[str, Any]],
    created_tokens: dict[str, str],
    store: Any,
) -> list[dict[str, Any]]:
    """Build phase_incomplete's `children` entries.

    Delivers a token to each pending child that hasn't proven it received
    one (RAISE-15740). A child gets a token from exactly one of two
    sources: `created_tokens` (its own just-minted token, freshly delivered
    in this same response) or a one-shot re-mint via
    `_remint_unused_child_token` (recovery when an earlier delivery was
    lost). Children that already advanced a phase, or that already used
    their one re-mint, get none.
    """
    entries: list[dict[str, Any]] = []
    for c in pending:
        entry = {
            "run_id": c["run_id"],
            "issue_id": c.get("issue_id", ""),
            "status": c.get("status", ""),
            "phase": _current_phase_id(c),
        }
        token = created_tokens.get(c["run_id"]) or await _remint_unused_child_token(
            c, store
        )
        if token is not None:
            entry["advance_token"] = token
        entries.append(entry)
    return entries


async def _create_missing_fanout_children(
    run: dict[str, Any],
    snapshot: list[str],
    child_pipeline_name: str,
    phase_id: str,
    store: Any,
    cwd: str,
) -> dict[str, str]:
    """Create a child for any snapshot key without one yet.

    Returns each new child's show-once advance_token by run_id, so the
    caller can deliver it directly in the same phase_incomplete response
    (RAISE-15740) instead of discarding it.
    """
    parent_run_id = run["run_id"]
    created_tokens: dict[str, str] = {}
    for key in snapshot:
        existing = await _find_child_run(store, parent_run_id, phase_id, key)
        if existing is None:
            result = await _create_child_run(
                run, child_pipeline_name, phase_id, store, cwd, fanout_key=key
            )
            token = result.get("advance_token")
            if result.get("child_run_id") and isinstance(token, str):
                created_tokens[result["child_run_id"]] = token
    return created_tokens


async def _dispatch_foreach(
    run: dict[str, Any],
    current_phase: dict[str, Any],
    child_pipeline_name: str,
    store: Any,
    cwd: str,
) -> dict[str, Any] | None:
    """Fan-out sub-pipeline: one child per story key from scope.md."""
    from raise_cli.pipeline.epic_story_iteration import (
        find_epic_scope_file,
        is_story_run_complete,
        parse_epic_story_rows,
    )

    parent_run_id = run["run_id"]
    phase_id = current_phase["id"]
    issue_id = run.get("issue_id", "")
    metadata = run.get("metadata", {})

    # Snapshot story keys on first advance (immutable after creation)
    snapshot: list[str] | None = metadata.get("fanout_snapshot")
    if snapshot is None:
        search_root = Path(cwd) if cwd else Path.cwd()
        scope_file = find_epic_scope_file(search_root, issue_id)
        if scope_file is None:
            return {
                "status": "error",
                "reason": f"foreach: stories requires scope.md for {issue_id}",
                "run_id": parent_run_id,
            }
        rows = parse_epic_story_rows(scope_file)
        snapshot = [jira_key for _, _, jira_key in rows if jira_key]
        if not snapshot:
            return {
                "status": "error",
                "reason": f"No story Jira keys found in scope.md for {issue_id}",
                "run_id": parent_run_id,
            }
        metadata["fanout_snapshot"] = snapshot
        await store.save(run)

    created_tokens = await _create_missing_fanout_children(
        run, snapshot, child_pipeline_name, phase_id, store, cwd
    )

    # Gather all children for this phase
    all_runs = await store.list_runs()
    children = [
        r
        for r in all_runs
        if r.get("metadata", {}).get("parent_run_id") == parent_run_id
        and r.get("metadata", {}).get("parent_phase") == phase_id
    ]

    # Check for failures (all_success policy) — reconcile against completed
    # replacement runs before blocking (RAISE-15108).
    failed = [c for c in children if c.get("status") in ("failed", "cancelled")]
    reconciled_ids: set[str] = set()
    if failed:
        all_runs = await store.list_runs()
        completed_story_keys = {
            r["issue_id"]
            for r in all_runs
            if r.get("pipeline_name") == "story"
            and is_story_run_complete(r)
            and r.get("issue_id")
        }
        truly_failed = [
            c
            for c in failed
            if c.get("metadata", {}).get("fanout_key") not in completed_story_keys
        ]
        reconciled_ids = {c["run_id"] for c in failed} - {
            c["run_id"] for c in truly_failed
        }
        if truly_failed:
            return {
                "status": "child_failed",
                "failed_count": len(truly_failed),
                "total_count": len(snapshot),
                "message": (
                    f"{len(truly_failed)} of {len(snapshot)} story pipelines failed — "
                    f"parent phase '{phase_id}' blocked by all_success policy."
                ),
                "run_id": parent_run_id,
            }

    # Check for pending — exclude reconciled cancelled/failed children
    pending = [
        c
        for c in children
        if not is_story_run_complete(c) and c["run_id"] not in reconciled_ids
    ]
    if pending:
        pending_entries = await _pending_child_entries(pending, created_tokens, store)
        return {
            "status": "phase_incomplete",
            "pending_count": len(pending),
            "total_count": len(snapshot),
            "current_phase": phase_id,
            "message": (
                f"{len(pending)} of {len(snapshot)} story pipelines still running."
            ),
            "children": pending_entries,
            "run_id": parent_run_id,
        }

    # All complete → store manifests and fall through
    for child in children:
        _store_child_manifest(run, child)
    return None


def _current_phase_id(run: dict[str, Any]) -> str:
    """Return the current phase id for a run dict."""
    idx = run.get("current_phase_index", 0)
    phases = run.get("phases", [])
    if idx < len(phases):
        return phases[idx].get("id", "?")
    return "?"


def _is_legacy_default_bugfix_pir(run: dict[str, Any], phase: dict[str, Any]) -> bool:
    """Return whether a serialized default run contains the retired PIR phase."""
    return (
        run.get("pipeline_name") == "bugfix"
        and phase.get("id") == "pir"
        and phase.get("skill") == "rai-bugfix-pir"
    )


async def _bypass_legacy_default_bugfix_pir(
    *,
    run: dict[str, Any],
    phases: list[dict[str, Any]],
    phase_index: int,
    store: Any,
    run_id: str,
    search_root: Path | None,
) -> str:
    """Skip a pre-RAISE-15375 PIR phase and record the migration in the run."""
    current = phases[phase_index]
    now = datetime.now(UTC).isoformat()
    bypass = {
        "phase": current["id"],
        "reason": "incompatible_default_bugfix_pir",
        "at": now,
    }
    current["status"] = "skipped"
    current["completed_at"] = now
    current["phase_bypass"] = bypass

    metadata = run.setdefault("metadata", {})
    bypasses = metadata.setdefault("phase_bypasses", [])
    if isinstance(bypasses, list):
        bypasses.append(bypass)
    else:
        metadata["phase_bypasses"] = [bypass]

    next_index = phase_index + 1
    if next_index >= len(phases):
        run["current_phase_index"] = next_index
        run["status"] = "complete"
        run["completed_at"] = now
        await store.save(run)
        return json.dumps(
            {
                "status": "complete",
                "message": "Pipeline complete after legacy PIR bypass.",
                "run_id": run_id,
                "phase_bypass": bypass,
            }
        )

    run["current_phase_index"] = next_index
    next_phase = phases[next_index]
    next_phase["started_at"] = now
    next_deterministic = await _execute_mcp_deterministic_phase(
        next_phase,
        str(search_root) if search_root else "",
        checkpoint=lambda: _checkpoint_run(store, run),
    )
    if next_deterministic and next_deterministic.get("status") == "failed":
        next_phase["status"] = "failed"
        run["status"] = "failed"
    await store.save(run)

    if run.get("status") == "failed":
        return json.dumps(
            {
                "status": "deterministic_failed",
                "run_id": run_id,
                "current_phase": next_phase["id"],
                "execution": next_deterministic,
                "phase_bypass": bypass,
            }
        )

    issue_id: str = run["issue_id"]
    skill: str | None = next_phase.get("skill")
    advance_model: str | None = next_phase.get("resolved_model")
    if advance_model is None:
        advance_model = _resolve_skill_model(
            skill,
            str(search_root) if search_root else "",
            phase_path=next_phase.get("phase_path"),
            phase_model=next_phase.get("model"),
        )
    agent_session_id = (
        run.get("metadata", {}).get("agent_session_id") or discover_agent_session_id()
    )
    context = _build_phase_context(
        next_phase["id"],
        skill or "",
        run,
        context_spec=next_phase.get("context_spec"),
        search_root=search_root,
    )
    instruction = _phase_instruction(
        skill,
        issue_id,
        advance_model,
        harness=_resolve_harness(next_phase, str(search_root) if search_root else ""),
        run_id=run_id,
        phase_id=next_phase["id"],
        parent_session=agent_session_id,
        skill_base=search_root / ".claude" / "skills" if search_root else None,
    )
    if next_deterministic is not None:
        instruction = (
            "Deterministic commands executed successfully; call "
            "pipeline_advance to complete the phase."
        )
    result: dict[str, Any] = {
        "status": "ok",
        "phase_number": next_index + 1,
        "total_phases": len(phases),
        "current_phase": next_phase["id"],
        "instruction": instruction,
        "skill": skill,
        "gate": next_phase.get("gate_type"),
        "context": context,
        "agent_session_id": agent_session_id,
        "rai_meta": {
            "run_id": run_id,
            "pipeline_name": run["pipeline_name"],
            "phase": next_phase["id"],
            "agent_session_id": agent_session_id,
        },
        "phase_bypass": bypass,
    }
    result.update(_phase_execution_contract(next_phase, advance_model))
    return json.dumps(result)


async def _advance_once(  # noqa: C901  -- MCP tool fan-out across run/phase states (cancelled/paused/complete, artifact validation, gate pending/approved); splitting breaks single-invocation contract
    run_id: str,
    *,
    approve: bool,
    cwd: str,
    advance_token: str = "",
    expected_phase: str = "",
) -> str:
    from raise_cli.pipeline.lease_enforcement import enforce

    store = get_run_store()

    # RAISE-13580 (AR N2): verify advance authority BEFORE enforce(renew=True)
    # so an unauthorized caller triggers no lease renewal. The hash-bearing run
    # is not otherwise loaded until after enforce, so do a cheap early load for
    # the authority check only; the retry loop already reloads (double-load is
    # accepted). A missing run falls through to the normal not-found handling.
    _auth_run = await store.load(run_id)
    if _auth_run is not None:
        refusal = _verify_run_authority(_auth_run, advance_token)
        if refusal is not None:
            return json.dumps(refusal)

    decision = enforce(cwd, renew=True)
    if decision.status == "rejected":
        return json.dumps(decision.to_payload())

    maintenance = _check_maintenance_lock()
    if maintenance:
        return json.dumps(maintenance)

    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    # Cancelled runs cannot advance
    if run.get("status") == "cancelled":
        return json.dumps({"status": "error", "reason": f"Run {run_id} is cancelled"})

    # Paused runs resume on advance without completing their current phase.
    resuming = run.get("status") == "paused"
    if resuming:
        run["status"] = "running"

    idx: int = run["current_phase_index"]
    phases = _get_phases(run)

    if idx >= len(phases):
        return json.dumps(
            {"status": "complete", "message": "Pipeline already complete"}
        )

    current = phases[idx]

    # D5 (RAISE-15030): expected-phase guard — reject if caller's expectation differs
    if expected_phase and current["id"] != expected_phase:
        return json.dumps(
            {
                "status": "phase_mismatch",
                "expected_phase": expected_phase,
                "current_phase": current["id"],
                "run_id": run_id,
            }
        )

    if resuming:
        await store.save(run)
        result: dict[str, Any] = {
            "status": "ok",
            "run_id": run_id,
            "resumed": True,
            "phase_number": idx + 1,
            "total_phases": len(phases),
            "current_phase": current["id"],
            "gate": current.get("gate_type"),
        }
        result.update(_restored_phase_dispatch(run, current, run_id))
        return json.dumps(result)

    # D5/S15457.2: caller root resolution chain — explicit cwd → run-metadata
    # start_cwd → structured cwd_required error (never the server process CWD).
    _start_cwd: str = run.get("metadata", {}).get("start_cwd", "")
    _root_or_err = _caller_context.resolve_run_cwd(cwd, _start_cwd, "pipeline_advance")
    if isinstance(_root_or_err, dict):
        return json.dumps(_root_or_err)
    search_root: Path = _root_or_err

    if current.get("type") == "deterministic" and current.get("commands"):
        deterministic_execution = current.get("deterministic_execution")
        if not isinstance(deterministic_execution, dict):
            return json.dumps(
                {
                    "status": "deterministic_not_executed",
                    "current_phase": current["id"],
                    "run_id": run_id,
                }
            )
        if deterministic_execution.get("status") != "passed":
            return json.dumps(
                {
                    "status": "deterministic_failed",
                    "current_phase": current["id"],
                    "execution": deterministic_execution,
                    "run_id": run_id,
                }
            )

    if _is_legacy_default_bugfix_pir(run, current):
        return await _bypass_legacy_default_bugfix_pir(
            run=run,
            phases=phases,
            phase_index=idx,
            store=store,
            run_id=run_id,
            search_root=search_root,
        )

    # Composite phase dispatch (S15078.2): when the current phase declares
    # `pipeline: X`, delegate to a child PipelineRun instead of running
    # artifact validation / gates on the parent directly.
    _child_pipeline: str | None = current.get("pipeline")
    if _child_pipeline is not None:
        _composite_result = await _dispatch_composite(
            run, current, _child_pipeline, store, str(search_root)
        )
        if _composite_result is not None:
            return json.dumps(_composite_result)
        # _dispatch_composite returns None when the child is complete and
        # the parent phase should be marked done — fall through to the
        # normal phase-completion flow below.

    # Artifact validation: check required artifacts exist before gate
    validates: list[dict[str, Any]] = current.get("validates", [])
    found_artifacts: list[str] = []
    run_issue_id: str = run.get("issue_id") or ""
    phase_started_at: str = current.get("started_at", "")
    if validates:
        all_present, missing, found_artifacts = _validate_artifacts(
            validates,
            search_root=search_root,
            issue_id=run_issue_id,
            phase_started_at=phase_started_at,
        )
        if not all_present:
            return json.dumps(
                {
                    "status": "artifact_missing",
                    "current_phase": current["id"],
                    "missing": missing,
                    "message": f"Phase '{current['id']}' requires artifacts before advancing. See 'missing' list.",
                    "run_id": run_id,
                }
            )

    # Gate validation: HITL gates block until explicitly approved.
    # Exception (ADR-093 K2): impact=low gates auto-approve with recorded
    # evidence — artifact validation above still applies (RAISE-3180).
    auto_approved: dict[str, Any] | None = None
    if current.get("gate_type") == "hitl" and not approve:
        if current.get("gate_impact") == "low":
            auto_approved = {
                "phase": current["id"],
                "impact": "low",
                "at": datetime.now(UTC).isoformat(),
                "reason": "impact=low policy (ADR-093 K2)",
            }
            current["auto_approved"] = auto_approved
        else:
            # RAISE-15048: stamp awaiting_gate so the cockpit (P2) can render
            # "⏸ phase (gate)" without polling. Blocked runs mutate nothing
            # else, so this is the one write worth persisting on this path.
            _stamp_awaiting_gate(run, current["id"])
            await store.save(run)
            return json.dumps(
                {
                    "status": "gate_pending",
                    "gate": "hitl",
                    "current_phase": current["id"],
                    "message": f"Phase '{current['id']}' has HITL gate — call pipeline_advance with approve=True to proceed.",
                    "run_id": run_id,
                }
            )

    # Proof-of-work: when approve=True on HITL gate, require that the
    # phase has validates configured AND they all produce results.
    # Without validates, there's no way to prove the skill executed.
    # (RAISE-3180 — prevent silent skill-skip)
    # Deterministic phases usually treat human approval as proof, but
    # epic story-iteration is special: approval must also prove that
    # the epic's child stories are actually complete. (RAISE-10936)
    if current.get("gate_type") == "hitl" and approve:
        if validates:
            all_present, missing, found_artifacts = _validate_artifacts(
                validates,
                search_root=search_root,
                issue_id=run_issue_id,
                phase_started_at=phase_started_at,
            )
            if not all_present:
                return json.dumps(
                    {
                        "status": "gate_proof_required",
                        "gate": "hitl",
                        "current_phase": current["id"],
                        "missing": missing,
                        "message": (
                            f"Phase '{current['id']}' requires artifacts matching "
                            "'validates' patterns before gate can be approved. "
                            "See 'missing' list."
                        ),
                        "run_id": run_id,
                    }
                )
        elif current.get("type") != "deterministic":
            return json.dumps(
                {
                    "status": "gate_proof_required",
                    "gate": "hitl",
                    "current_phase": current["id"],
                    "message": (
                        f"Phase '{current['id']}' has HITL gate but no 'validates' "
                        "configured. Add validates entries to the phase definition "
                        "in the pipeline YAML to prove the skill was executed."
                    ),
                    "run_id": run_id,
                }
            )

        # S14770.9: "epic" is now the default pipeline; enterprise epic renamed to "epic-enterprise"
        if (
            run["pipeline_name"] in ("epic", "epic-enterprise")
            and current["id"] == "story-iteration"
        ):
            pending_stories, blocking_reason = await pending_epic_stories(
                search_root,
                run_issue_id,
                run_store=store,
            )
            if blocking_reason is not None or pending_stories:
                reason = blocking_reason or "child stories still incomplete"
                return json.dumps(
                    {
                        "status": "phase_incomplete",
                        "current_phase": current["id"],
                        "pending_stories": pending_stories,
                        "message": (
                            f"Epic '{run_issue_id}' cannot leave story-iteration: "
                            f"{reason}."
                        ),
                        "run_id": run_id,
                    }
                )

    # Workflow-point enforcement (RAISE-12207): a phase may bind itself to a
    # before-point via `workflow_point`. Emitting it in-process routes through
    # GateBridgeHook -> run_gates_for_point, making the point-bound gates
    # engine-forced rather than skill-prose-forced. This is a precondition to
    # marking the phase done: on abort we return a blocking `gate_failed` and
    # leave phase/run state untouched so the agent can remediate and re-advance
    # (gates re-run; idempotent). working_dir MUST be the run's resolved
    # search_root (not the MCP server's Path.cwd()) so gates run against the
    # caller's checkout — see gate_bridge.py:47-54.
    _workflow_point: str | None = current.get("workflow_point")
    if _workflow_point:
        from raise_cli.hooks.emitter import create_emitter
        from raise_cli.hooks.events import (
            BeforeBugCloseEvent,
            BeforeInitiativeConcludedEvent,
            BeforeInitiativeValidatedEvent,
            BeforeStoryCloseEvent,
        )

        # S14263.6 (RAISE-14712): workflow points listed here are advisory —
        # the engine emits the event (gates run and log) but never aborts the
        # pipeline on gate failure. Mirrors CI allow_failure:true (ADR-130 D2).
        _wp_advisory: frozenset[str] = frozenset({"before:story:close"})

        _wp_event_map: dict[str, Any] = {
            "before:bug:close": BeforeBugCloseEvent,
            "before:initiative:validated": BeforeInitiativeValidatedEvent,
            "before:initiative:concluded": BeforeInitiativeConcludedEvent,
            "before:story:close": BeforeStoryCloseEvent,
        }
        _event_cls = _wp_event_map.get(_workflow_point)
        if _event_cls is not None:
            _wp_working_dir = str(search_root)
            # RAISE-12207: pass the agent session id captured at pipeline_start
            # (falling back to a fresh discovery) so the point-bound session-
            # scoped gate (gate-ar-bugfix) resolves the marker under the agent's
            # session, not the MCP-server process env.
            _wp_session_id = (
                run.get("metadata", {}).get("agent_session_id")
                or discover_agent_session_id()
            )
            _emit_result = create_emitter().emit(
                _event_cls(
                    issue_id=run_issue_id,
                    working_dir=_wp_working_dir,
                    session_id=_wp_session_id,
                )
            )
            if _emit_result.aborted and _workflow_point not in _wp_advisory:
                return json.dumps(
                    {
                        "status": "gate_failed",
                        "current_phase": current["id"],
                        "workflow_point": _workflow_point,
                        "message": _emit_result.abort_message,
                        "run_id": run_id,
                    }
                )

    # quality_gates execution (RAISE-14934 T5): declarative gates run after
    # workflow_point enforcement; blocking failure prevents phase from completing.
    # NOTE (RAISE-16254): unused seam — superseded by raise_task_complete.
    _quality_gates: list[str] = current.get("quality_gates") or []
    if _quality_gates:
        from raise_cli.gates.execution import blocking_failures, run_gates_by_id

        _qg_wd = search_root
        _qg_sid = (
            run.get("metadata", {}).get("agent_session_id")
            or discover_agent_session_id()
        )
        _qg_results = run_gates_by_id(_quality_gates, _qg_wd, session_id=_qg_sid)
        _qg_gate_mode = (
            "advisory" if current.get("gate_mode") == "advisory" else "blocking"
        )
        _qg_blocking = blocking_failures(_qg_results, _qg_gate_mode)
        if _qg_blocking:
            return json.dumps(
                {
                    "status": "gate_failed",
                    "current_phase": current["id"],
                    "quality_gates": [r.gate_id for r in _qg_blocking],
                    "message": "; ".join(
                        f"{r.gate_id}: {r.message}" for r in _qg_blocking
                    ),
                    "run_id": run_id,
                }
            )

    # Decision journal (RAISE-15048 / design §2.1): stamp the HITL resolution
    # now that every proof-of-work / workflow-point / quality-gate check above
    # has passed and the phase is guaranteed to complete below. Also clears
    # any stale awaiting_gate — a completing phase is never "awaiting" again
    # (Sol S7/R4).
    if current.get("gate_type") == "hitl":
        if auto_approved is not None:
            _append_hitl_decision(
                run, "auto-approved (impact=low)", current["id"], source="auto"
            )
            _emit_mcp_hitl_decision(
                run, phase_id=current["id"], decision="auto_approve", actor_kind="auto"
            )
        elif approve:
            _append_hitl_decision(run, "approved", current["id"], source="gate")
            _emit_mcp_hitl_decision(
                run, phase_id=current["id"], decision="approve", actor_kind="gate"
            )
    run.get("metadata", {}).pop("awaiting_gate", None)

    # Mark current phase as done
    current["status"] = "done"
    current["completed_at"] = datetime.now(UTC).isoformat()

    # Backlog transition (D2, RAISE-15030) — advisory, fail-open; result stored on phase
    _t_target: str | None = current.get("target_status")
    _t_issue: str = run_issue_id or run.get("issue_id") or ""
    if _t_target and _t_issue:
        from raise_cli.pipeline.transitions import (
            apply_phase_transition_async,
            resolve_transition_deps,
        )

        _t_cwd = search_root
        _t_adapter, _t_machine = resolve_transition_deps(_t_cwd)
        _t_record = await apply_phase_transition_async(
            phase_id=current["id"],
            target_status=_t_target,
            issue_key=_t_issue,
            adapter=_t_adapter,
            machine=_t_machine,
        )
        current["backlog_transition"] = _t_record.model_dump(mode="json")
        if _t_record.outcome == "applied":
            import contextlib

            from raise_cli.hooks.emitter import create_emitter
            from raise_cli.hooks.events import BacklogTransitionEvent

            with contextlib.suppress(Exception):
                create_emitter().emit(
                    BacklogTransitionEvent(
                        run_id=run["run_id"],
                        phase_id=_t_record.phase_id,
                        issue_key=_t_record.issue_key,
                        from_status=_t_record.from_status,
                        to_slug=_t_record.to_slug,
                    )
                )

    # RAISE-15567: post-transition gates validate effects that cannot be true
    # before the write (for bug close: Jira status_category == "done").
    if _t_target and _t_issue and _workflow_point:
        from raise_cli.pipeline.engine import (
            PipelineEngine,
            post_transition_workflow_point,
        )

        _post_point = post_transition_workflow_point(_workflow_point)
        if _post_point and not PipelineEngine.enforce_workflow_point(
            _post_point,
            _t_issue,
            search_root,
            run.get("metadata", {}).get("agent_session_id"),
        ):
            current["status"] = "pending"
            current.pop("completed_at", None)
            await store.save(run)
            return json.dumps(
                {
                    "status": "gate_failed",
                    "current_phase": current["id"],
                    "workflow_point": _post_point,
                    "message": f"Workflow-point gates failed: {_post_point}",
                    "run_id": run_id,
                }
            )

    # K3 (S7884.5): lifecycle complete for the closing phase — server-side,
    # never an LLM turn. Suppressed on failure (ADR-039).
    from contextlib import suppress as _suppress

    with _suppress(Exception):
        _emit_lifecycle(
            run["pipeline_name"],
            run["issue_id"],
            "complete",
            current["id"],
            cwd=search_root,
        )

    # Capture git stats when implement phase completes (fire-and-forget).
    # S15457.2: resolved via the cwd → start_cwd → error chain above — never
    # the MCP server CWD. Both the project_id key AND `git branch
    # --show-current` run in the RUN's own checkout.
    if current["id"] == "implement":
        _stats_task = asyncio.create_task(
            _populate_story_stats(search_root, run["issue_id"])
        )
        _BACKGROUND_TASKS.add(_stats_task)
        _stats_task.add_done_callback(_BACKGROUND_TASKS.discard)

    # Calculate duration
    started = current.get("started_at", "")
    duration = 0.0
    if started:
        try:
            start_dt = datetime.fromisoformat(started)
            end_dt = datetime.fromisoformat(current["completed_at"])
            duration = (end_dt - start_dt).total_seconds()
        except (ValueError, TypeError):
            pass

    # Phase finish report (ADR-062 — fire-and-forget)
    # S15457.2: resolved via the cwd → start_cwd → error chain above so
    # telemetry resolves the worktree CC session, not the MCP server CWD.
    # RAISE-15783: bridge MCP telemetry gap — CLAUDE_CODE_SESSION_ID is not set
    # in the MCP server process, so adapter discovery returns NullTelemetryAdapter
    # (cost=0). Instead, resolve the CC JSONL from agent_session_id stored at
    # pipeline_start time (when CC vars ARE available via the Bash tool).
    _telemetry_root = search_root
    _phase_report: PhaseFinishReport | None = None
    _started_at: datetime | None = None
    # RAISE-16237: `executed` must distinguish "agent ran" from "gate
    # bypassed without proof". Two independent ways to know proof-of-work
    # happened:
    #   1. `auto_approved is None` — the phase never hit the impact=low
    #      bypass at all. It advanced via approve=True (which already
    #      required validated artifacts above, see gate_proof_required) or
    #      it isn't a gated phase (the agent self-reports completion).
    #   2. `bool(validates)` — the phase DID hit the impact=low auto-approve
    #      bypass (ADR-093 K2), but declares `validates`. Artifact
    #      validation above (~line 2651) runs BEFORE the gate branch and
    #      applies on every path, gated or not, so reaching here with a
    #      non-empty `validates` means `_validate_artifacts` already
    #      passed — a genuine proof-of-work signal, not an inference from
    #      cost/model telemetry (still forbidden per the original issue).
    # executed=False therefore means precisely "advanced with neither an
    # agent-reported completion nor artifact proof": an impact=low bypass
    # on a phase with no `validates` configured at all — fail-safe, and
    # the only case where nothing here can vouch that an agent ran.
    _executed = auto_approved is None or bool(validates)
    try:
        _started_at = datetime.fromisoformat(started) if started else None
        _completed_at = datetime.fromisoformat(current["completed_at"])
        _session_id = run.get("metadata", {}).get("agent_session_id", "")
        _jsonl_path = find_cc_jsonl_by_session_id(_session_id) if _session_id else None
        if _jsonl_path is not None:
            from raise_cli.telemetry.cc_adapter import ClaudeCodeTelemetryAdapter

            _phase_report = phase_finish_report(
                _telemetry_root,
                phase=current["id"],
                pipeline_name=run["pipeline_name"],
                run_id=run_id,
                started_at=_started_at,
                completed_at=_completed_at,
                issue=run.get("issue_id"),
                session_data_override=_jsonl_path,
                adapter=ClaudeCodeTelemetryAdapter(),
                executed=_executed,
            )
        else:
            _phase_report = phase_finish_report(
                _telemetry_root,
                phase=current["id"],
                pipeline_name=run["pipeline_name"],
                run_id=run_id,
                started_at=_started_at,
                completed_at=_completed_at,
                issue=run.get("issue_id"),
                executed=_executed,
            )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("Phase finish report failed", exc_info=True)

    # Emit phase_finish event to server (fire-and-forget, S9115.3)
    if _phase_report is not None:
        try:
            from raise_cli.telemetry.emitter import (
                UnifiedEmitter,
                load_raise_env_from_bashrc,
            )
            from raise_cli.telemetry.phase_report import build_phase_finish_event

            load_raise_env_from_bashrc()
            event = build_phase_finish_event(_phase_report)
            emitter = UnifiedEmitter(project_root=_telemetry_root)
            emitter.post_direct(event)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            _log.debug("Phase finish event emission failed", exc_info=True)

    # Advance to next phase, skipping size-gated phases (proportionality aspect,
    # ADR-116). The MCP advance path honors ONLY the `size >= …` predicate — other
    # `when` conditions (e.g. story_type) stay engine-only, because their metadata
    # is not wired into this path and activating them here would silently skip
    # phases for every run. Reuses engine.evaluate_when for the size semantics
    # (missing size → fail-safe full ceremony).
    from raise_cli.pipeline.engine import evaluate_when

    _metadata: dict[str, str] = run.get("metadata", {})
    next_idx = idx + 1
    while next_idx < len(phases):
        _nxt = phases[next_idx]
        _when = _nxt.get("when")
        if (
            _when
            and _when.strip().startswith("size")
            and not evaluate_when(_when, _metadata)
        ):
            _nxt["status"] = "skipped"
            _nxt["completed_at"] = datetime.now(UTC).isoformat()
            next_idx += 1
            continue
        break

    if next_idx >= len(phases):
        run["current_phase_index"] = next_idx
        run["status"] = "complete"
        run["completed_at"] = datetime.now(UTC).isoformat()
        await store.save(run)
        from raise_cli.pipeline.worktree_lock import unlock_worktree

        unlock_worktree(run.get("metadata", {}).get("locked_worktree"))
        # Emit telemetry for final phase (fire-and-forget)
        try:
            emit_phase_transition(
                pipeline_name=run["pipeline_name"],
                run_id=run_id,
                issue=run["issue_id"],
                phase_completed=current["id"],
                phase_next=None,
                duration_seconds=duration,
                gate_type=current.get("gate_type"),
                gate_result=(
                    "approved"
                    if approve
                    else ("auto-approved" if auto_approved else None)
                ),
                context_nodes=0,
                mission_id=_detect_mission_id(),
                event_emitter=_get_event_emitter(search_root),
            )
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            _log.debug("Telemetry emission failed", exc_info=True)
        done_count = sum(1 for p in phases if p["status"] == "done")
        complete_result: dict[str, Any] = {
            "status": "complete",
            "message": f"Pipeline complete. {done_count}/{len(phases)} phases done.",
            "run_id": run_id,
        }
        if _phase_report is not None:
            complete_result["phase_report"] = _phase_report.model_dump()
            complete_result["phase_summary"] = format_phase_summary(_phase_report)
        if current.get("backlog_transition"):  # D4
            complete_result["backlog_transition"] = current["backlog_transition"]
        return json.dumps(complete_result)

    run["current_phase_index"] = next_idx
    phase = phases[next_idx]
    phase["started_at"] = datetime.now(UTC).isoformat()
    next_deterministic = await _execute_mcp_deterministic_phase(
        phase,
        str(search_root),
        checkpoint=lambda: _checkpoint_run(store, run),
    )
    if next_deterministic and next_deterministic.get("status") == "failed":
        phase["status"] = "failed"
        run["status"] = "failed"
        await store.save(run)
        from raise_cli.pipeline.worktree_lock import unlock_worktree

        unlock_worktree(run.get("metadata", {}).get("locked_worktree"))
        return json.dumps(
            {
                "status": "deterministic_failed",
                "run_id": run_id,
                "current_phase": phase["id"],
                "execution": next_deterministic,
            }
        )
    await store.save(run)
    # K3 (S7884.5): lifecycle start for the opening phase.
    with _suppress(Exception):
        _emit_lifecycle(
            run["pipeline_name"],
            run["issue_id"],
            "start",
            phase["id"],
            cwd=search_root,
        )
    issue_id: str = run["issue_id"]
    skill: str | None = phase.get("skill")
    context_skill = skill or ""

    context = _build_phase_context(
        phase["id"],
        context_skill,
        run,
        context_spec=phase.get("context_spec"),
        search_root=search_root,
    )

    # Emit telemetry for completed phase (fire-and-forget)
    try:
        emit_phase_transition(
            pipeline_name=run["pipeline_name"],
            run_id=run_id,
            issue=run["issue_id"],
            phase_completed=current["id"],
            phase_next=phase["id"],
            duration_seconds=duration,
            gate_type=current.get("gate_type"),
            gate_result=(
                "approved" if approve else ("auto-approved" if auto_approved else None)
            ),
            context_nodes=len(context),
            mission_id=_detect_mission_id(),
            event_emitter=_get_event_emitter(search_root),
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("Telemetry emission failed", exc_info=True)

    advance_model: str | None = phase.get("resolved_model")
    if advance_model is None:
        advance_model = _resolve_skill_model(
            skill,
            cwd,
            phase_path=phase.get("phase_path"),
            phase_model=phase.get("model"),
        )
    _advance_session_id = (
        run.get("metadata", {}).get("agent_session_id") or discover_agent_session_id()
    )
    instruction = _phase_instruction(
        skill,
        issue_id,
        advance_model,
        harness=_resolve_harness(phase, cwd),
        run_id=run_id,
        phase_id=phase["id"],
        parent_session=_advance_session_id,
        skill_base=Path(cwd) / ".claude" / "skills" if cwd else None,
    )
    if next_deterministic is not None:
        instruction = (
            "Deterministic commands executed successfully; call "
            "pipeline_advance to complete the phase."
        )
    result: dict[str, Any] = {
        "status": "ok",
        "phase_number": next_idx + 1,
        "total_phases": len(phases),
        "current_phase": phase["id"],
        "instruction": instruction,
        "skill": skill,
        "gate": phase.get("gate_type"),
        "context": context,
        "agent_session_id": _advance_session_id,
        "rai_meta": {
            "run_id": run_id,
            "pipeline_name": run["pipeline_name"],
            "phase": phase["id"],
            "agent_session_id": _advance_session_id,
        },
    }
    result.update(_phase_execution_contract(phase, advance_model))
    if auto_approved:
        result["auto_approved"] = auto_approved
    if phase.get("review_mode"):
        result["review_mode"] = phase["review_mode"]
        result["review_template"] = phase.get("review_template")
    if found_artifacts:
        result["previous_artifacts"] = found_artifacts
    if _phase_report is not None:
        result["phase_report"] = _phase_report.model_dump()
        result["phase_summary"] = format_phase_summary(_phase_report)
    guardrails_data = _evaluate_guardrails(str(search_root), started_at=_started_at)
    if guardrails_data is not None:
        result["guardrails"] = guardrails_data
    if current.get("backlog_transition"):  # D3
        result["backlog_transition"] = current["backlog_transition"]
    return json.dumps(result)


@mcp.tool()
async def pipeline_pause(run_id: str, cwd: str = "") -> str:
    """Pause a pipeline run. The run can be resumed by calling pipeline_advance.

    Args:
        run_id: The run ID returned by pipeline_start.
        cwd: Caller's checkout path. When provided with a server-asserted root
            (RAISE_PROJECT_ROOT / --project), the caller root must match or the
            request is rejected with worktree_mismatch (S15457.4).
    """
    identity_mismatch = _check_mcp_worktree_identity(cwd)  # S15457.4
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    store = get_run_store()
    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    if run.get("status") == "cancelled":
        return json.dumps(
            {"status": "error", "reason": f"Run {run_id} is cancelled — cannot pause"}
        )

    run["status"] = "paused"
    await store.save(run)
    idx: int = run["current_phase_index"]
    phases = _get_phases(run)

    return json.dumps(
        {
            "status": "paused",
            "run_id": run_id,
            "current_phase": phases[idx]["id"] if idx < len(phases) else "complete",
            "message": "Run paused. Call pipeline_advance to resume.",
        }
    )


@mcp.tool()
async def pipeline_cancel(run_id: str, cwd: str = "", force: bool = False) -> str:
    """Cancel a pipeline run. Cancelled runs cannot be resumed.

    Args:
        run_id: The run ID returned by pipeline_start.
        cwd: Caller's checkout path. When provided with a server-asserted root
            (RAISE_PROJECT_ROOT / --project), the caller root must match or the
            request is rejected with worktree_mismatch (S15457.4).
        force: Override ownership guard. Required to cancel a run whose
            worktree lease is held by another live session (RAISE-15802).
    """
    identity_mismatch = _check_mcp_worktree_identity(cwd)  # S15457.4
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    store = get_run_store()
    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    if not force:
        is_foreign, owner_desc = is_foreign_live_run(run)
        if is_foreign:
            return json.dumps(
                {
                    "status": "rejected",
                    "reason": f"Run owned by live foreign session: {owner_desc}",
                    "message": (
                        "Cannot cancel a run whose worktree lease is held by "
                        "another live session. Use force=True to override."
                    ),
                    "run_id": run_id,
                }
            )

    run["status"] = "cancelled"
    run["completed_at"] = datetime.now(UTC).isoformat()
    await store.save(run)
    from raise_cli.pipeline.worktree_lock import unlock_worktree

    unlock_worktree(run.get("metadata", {}).get("locked_worktree"))

    return json.dumps(
        {
            "status": "cancelled",
            "run_id": run_id,
            "message": "Run cancelled.",
        }
    )


@local_only
async def pipeline_restore(run_id: str, cwd: str = "") -> str:  # noqa: C901
    """Restore full pipeline state after compaction or restart.

    Returns run state + context for the current phase, plus a recovery block
    with lease acquisition status and reissue command when cwd is provided.

    Fix 1 (RAISE-15050 §3.2): When cwd is provided, acquires the worktree
    lease using enforce(cwd, renew=False) with the same ADR-094 fail-open
    semantics as pipeline_start. Acquiring the lease is a precondition for
    token reissue (gate a in pipeline token reissue checks lease.session_id).

    Crash-window re-check (AC7, RAISE-15026): After loading the run, checks
    whether the last completed phase had a target_status but no
    backlog_transition recorded (crash window: crashed after advancing phase
    but before transition was persisted). Reports as recovery_check for the
    agent to handle.

    Args:
        run_id: The run ID returned by pipeline_start.
        cwd: Working directory of the calling session. When provided, enforce()
            is called to acquire the worktree lease so that pipeline token
            reissue can verify gate (a). Omit for passive state inspection.
    """
    import shlex

    from raise_cli.pipeline.lease_enforcement import enforce

    identity_mismatch = _check_mcp_worktree_identity(cwd)  # S15457.4
    if identity_mismatch is not None:
        return json.dumps(identity_mismatch)

    store = get_run_store()
    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    idx: int = run["current_phase_index"]
    phases = _get_phases(run)
    current = phases[idx] if idx < len(phases) else None

    context: list[dict[str, Any]] = []
    if current:
        # RAISE-8470: resolve against the worktree the run was started from,
        # not the MCP server's CWD, so restored context re-reads the correct
        # checkout's artifacts.
        _start_cwd: str = run.get("metadata", {}).get("start_cwd", "")
        context = _build_phase_context(
            current["id"],
            current["skill"],
            run,
            context_spec=current.get("context_spec"),
            search_root=Path(_start_cwd) if _start_cwd else None,
        )

    restore_result: dict[str, Any] = {
        "run_id": run_id,
        "status": run.get("status", "running"),
        "pipeline_name": run["pipeline_name"],
        "issue_id": run["issue_id"],
        "current_phase": current["id"] if current else "complete",
        "completed_phases": [p["id"] for p in phases if p["status"] == "done"],
        "context": context,
        # RAISE-15048 / design §2.4: surface the decision journal on recovery.
        "decisions": run.get("metadata", {}).get("hitl_decisions", []),
    }
    if current:
        restore_result.update(_restored_phase_dispatch(run, current, run_id))
    if current and current.get("review_mode"):
        restore_result["review_mode"] = current["review_mode"]
        restore_result["review_template"] = current.get("review_template")

    # Fix 1 (RAISE-15050 §3.2): acquire worktree lease and build recovery block.
    if cwd:
        _effective_cwd = cwd  # cwd is guaranteed truthy here (inside `if cwd:`)
        decision = enforce(_effective_cwd, renew=False)
        recovery: dict[str, Any] = {}

        # discover_agent_session_id() returns the CURRENT session (not the stale
        # metadata.agent_session_id from the crashed run — Sol S2 fix).
        _current_sid = discover_agent_session_id()

        if decision.status == "allowed" and decision.worktree_id:
            # Lease acquired under the current session — token reissue can proceed.
            recovery["lease_status"] = "acquired"
            # RAISE-16907: auto-reissue when lockout detected (token-bearing,
            # advanceable, not cancelled).  Eliminates the two-command
            # restore-then-reissue flow that users cannot discover.
            # One-shot: stamps restored_reissue_at so repeat calls don't
            # rotate again (mirrors reminted_at in composite dispatch).
            _meta = run.get("metadata", {})
            _has_token = bool(_meta.get("advance_token_hash"))
            _not_cancelled = run.get("status") != "cancelled"
            _advanceable = idx < len(phases)
            _already_reissued = bool(_meta.get("restored_reissue_at"))
            if _has_token and _not_cancelled and _advanceable and not _already_reissued:
                new_token = secrets.token_urlsafe(16)
                _meta["advance_token_hash"] = hashlib.sha256(
                    new_token.encode()
                ).hexdigest()
                _meta["restored_reissue_at"] = datetime.now(UTC).isoformat()
                try:
                    await store.save(run)
                except OptimisticLockError:
                    _log.warning(
                        "pipeline_restore: write conflict during auto-reissue "
                        "for run %s — skipping; token NOT rotated",
                        run_id,
                    )
                else:
                    recovery["advance_token"] = new_token
                    _audit = logging.getLogger("raise.audit")
                    _audit.warning(
                        "pipeline.advance_token.restored_reissue "
                        "run_id=%s session_id=%s",
                        run_id,
                        _current_sid or "unknown",
                    )
            elif _current_sid:
                # Sol R1: shell-quote all path values (including session ID) to prevent injection.
                recovery["reissue_command"] = (
                    f"rai pipeline token reissue {run_id} "
                    f"--cwd {shlex.quote(_effective_cwd)} "
                    f"--session {shlex.quote(_current_sid)} "
                    f"--non-interactive"
                )
        else:
            # Sol S3: lease not acquired — degrade gracefully.
            recovery["lease_status"] = "not_acquired"
            recovery["lease_note"] = (
                "Could not acquire worktree lease — session identity not resolved or "
                "lease held by another session. "
                "Run 'rai pipeline token reissue' manually with "
                "--session <your-session-id> after verifying the lease is free."
            )
        restore_result["recovery"] = recovery

    # AC7 (RAISE-15050): crash-window re-check — verify the last completed phase's
    # backlog_transition against target_status; report as recovery_check if missing.
    # Crash window: agent crashed after _advance_once set phase["status"]="done" but
    # before calling store.save(run) — the Jira transition may have fired but the
    # record was not persisted. Report for agent/human follow-up.
    done_phases = [p for p in phases if p.get("status") == "done"]
    if done_phases:
        last_done = done_phases[-1]
        _tgt: str | None = last_done.get("target_status")
        _bt: dict[str, Any] | None = last_done.get("backlog_transition")
        if _tgt and not _bt:
            restore_result["recovery_check"] = {
                "phase": last_done["id"],
                "target_status": _tgt,
                "status": "missed_transition",
                "hint": (
                    f"Phase '{last_done['id']}' completed with target_status='{_tgt}' "
                    "but no backlog_transition was recorded — possible crash window. "
                    f"Verify {run.get('issue_id', '?')} is in '{_tgt}' in your backlog; "
                    "if not, transition it manually before resuming."
                ),
            }

    return json.dumps(restore_result)


@mcp.tool()
async def pipeline_status(run_id: str) -> str:
    """Get current status of a pipeline run.

    Args:
        run_id: The run ID returned by pipeline_start.
    """
    store = get_run_store()
    run = await store.load(run_id)
    if run is None:
        return json.dumps({"status": "error", "reason": f"Run {run_id} not found"})

    idx: int = run["current_phase_index"]
    phases = _get_phases(run)

    run_status = run.get("status", "running")

    all_runs = await store.list_runs()
    phase_entries: list[dict[str, Any]] = []
    for p in phases:
        entry: dict[str, Any] = {
            "id": p["id"],
            "status": p["status"],
            "gate": p.get("gate_type"),
        }
        if p.get("auto_approved"):
            entry["auto_approved"] = p["auto_approved"]
        if p.get("pipeline"):
            children = [
                r
                for r in all_runs
                if r.get("metadata", {}).get("parent_run_id") == run_id
                and r.get("metadata", {}).get("parent_phase") == p["id"]
            ]
            if children:
                entry["children"] = [
                    {
                        "run_id": c["run_id"],
                        "pipeline": c.get("pipeline_name", ""),
                        "issue": c.get("issue_id", ""),
                        "status": c.get("status", ""),
                        "phase": _current_phase_id(c),
                    }
                    for c in children
                ]
        phase_entries.append(entry)

    result_data: dict[str, Any] = {
        "run_id": run_id,
        "pipeline": run["pipeline_name"],
        "issue": run["issue_id"],
        "current_phase": phases[idx]["id"] if idx < len(phases) else "complete",
        "progress": f"{idx}/{len(phases)}",
        "phases": phase_entries,
    }
    if run_status in ("paused", "cancelled"):
        result_data["status"] = run_status
    return json.dumps(result_data)


@mcp.tool()
async def pipeline_runs() -> str:
    """List all active and recent pipeline runs."""
    store = get_run_store()
    all_runs = await store.list_runs()
    result: list[dict[str, Any]] = []
    for run in all_runs:
        idx: int = run["current_phase_index"]
        phases = _get_phases(run)
        entry: dict[str, Any] = {
            "run_id": run["run_id"],
            "pipeline": run["pipeline_name"],
            "issue": run["issue_id"],
            "progress": f"{idx}/{len(phases)}",
            "current_phase": phases[idx]["id"] if idx < len(phases) else "complete",
        }
        parent_id = run.get("metadata", {}).get("parent_run_id")
        if parent_id:
            entry["parent_run_id"] = parent_id
        run_status = run.get("status", "running")
        if run_status in ("paused", "cancelled"):
            entry["status"] = run_status
        result.append(entry)
    return compact_response(result)
