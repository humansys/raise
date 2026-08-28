"""Data models and fetching for context bundle assembly.

Contains data models (LiveBacklogStatus, SectionManifest), path constants,
and functions that load data from disk or external services.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol, cast

from pydantic import BaseModel

from raise_cli.graph.backends import get_active_backend
from raise_cli.schemas.session_state import CurrentWork, SessionState
from raise_cli.session.donor import DonorMismatch, DonorSource
from raise_core.graph.backends.protocol import (
    GraphBundleQueryBackend,
    GraphTraversalBackend,
)
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

GraphAttrs = dict[str, Any]


class _SupportsGraphLoad(Protocol):
    def load(self) -> Graph: ...


class LiveBacklogStatus(BaseModel):
    """Live status fetched from backlog adapter during session-start."""

    epic_status: str = ""
    epic_summary: str = ""
    story_status: str = ""
    story_summary: str = ""
    warning: str = ""


class SectionManifest(BaseModel):
    """Manifest entry for a queryable context section."""

    name: str
    count: int
    token_estimate: int


class BundleProvenance(BaseModel):
    """Compact source metadata for the session-start context bundle."""

    continuity_source: DonorSource = DonorSource.NONE
    continuity_session_id: str | None = None
    mission_id: str | None = None
    mission_source: str = "none"
    worktree_id: str | None = None
    worktree_source: str = "none"
    current_work_source: str = "none"
    mismatch: DonorMismatch | None = None


# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"
# Sessions index path relative to project root (personal = developer-specific)
SESSIONS_INDEX_REL_PATH = (
    Path(".raise") / "rai" / "personal" / "sessions" / "index.jsonl"
)


def fetch_live_status(
    state: SessionState | None,
    timeout: float = 5.0,
) -> LiveBacklogStatus:
    """Query backlog adapter for live epic/story status.

    Returns LiveBacklogStatus with warning on any failure.
    Never raises — all errors are caught and surfaced as warnings.
    """
    if state is None:
        return LiveBacklogStatus()

    epic_key = state.current_work.epic
    story_key = state.current_work.story

    if not epic_key and not story_key:
        return LiveBacklogStatus()

    return _query_adapter(epic_key, story_key, timeout)


def _query_adapter(
    epic_key: str,
    story_key: str,
    timeout: float,
) -> LiveBacklogStatus:
    """Resolve adapter and run queries with timeout. Never raises.

    The entire operation (adapter resolution + issue fetches) runs inside
    the ThreadPoolExecutor so that the timeout covers everything, including
    slow adapter startup (e.g., MCP bridge initialization).
    """
    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import TimeoutError as FuturesTimeoutError

    from raise_cli.adapters.models import IssueDetail
    from raise_cli.adapters.protocols import ProjectManagementAdapter
    from raise_cli.adapters.resolve import resolve_pm_adapter
    from raise_cli.exceptions import AdapterResolutionError

    def _do_fetch() -> LiveBacklogStatus:
        adapter: ProjectManagementAdapter = resolve_pm_adapter(None)
        result = LiveBacklogStatus()
        if epic_key:
            detail: IssueDetail = adapter.get_issue(epic_key)
            result.epic_status = detail.status
            result.epic_summary = detail.summary
        if story_key:
            detail = adapter.get_issue(story_key)
            result.story_status = detail.status
            result.story_summary = detail.summary
        return result

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_do_fetch)
            return future.result(timeout=timeout)
    except FuturesTimeoutError:
        logger.debug("Live status fetch timed out after %.1fs", timeout)
        return LiveBacklogStatus(
            warning=f"Backlog query timeout ({timeout:.0f}s) — showing cached state"
        )
    except AdapterResolutionError as exc:
        logger.debug("Adapter unavailable: %s", exc)
        return LiveBacklogStatus(
            warning=f"Adapter unavailable: {exc} — showing cached state"
        )
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Live status fetch failed: %s", exc)
        return LiveBacklogStatus(
            warning=f"Backlog query error: {exc} — showing cached state"
        )


def get_foundational_patterns(project_path: Path) -> list[GraphNode]:
    """Query memory graph for foundational patterns.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of pattern GraphNodes with foundational=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH

    try:
        backend = get_active_backend(graph_path, project_root=project_path)
        if isinstance(backend, GraphBundleQueryBackend):
            return backend.get_foundational_patterns()
        graph = backend.load()
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node
        for node in graph.iter_concepts()
        if node.type == "pattern" and node.metadata.get("foundational") is True
    ]


def get_always_on_primes(project_path: Path) -> list[GraphNode]:
    """Query memory graph for all always_on nodes (governance + identity).

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of GraphNodes with always_on=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH

    try:
        backend = get_active_backend(graph_path, project_root=project_path)
        if isinstance(backend, GraphBundleQueryBackend):
            return backend.get_always_on_nodes()
        graph = backend.load()
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node for node in graph.iter_concepts() if node.metadata.get("always_on") is True
    ]


def find_release_for_current_epic(project_path: Path, epic_id: str) -> GraphNode | None:
    """Find release node for the current epic from the memory graph.

    Args:
        project_path: Absolute path to the project root.
        epic_id: Epic identifier (e.g., "E19").

    Returns:
        The release GraphNode, or None if not found or graph unavailable.
    """
    if not epic_id:
        return None

    graph_path = project_path / GRAPH_REL_PATH

    try:
        from raise_core.graph.query import QueryEngine

        backend = get_active_backend(graph_path, project_root=project_path)
        if isinstance(backend, GraphBundleQueryBackend):
            return backend.find_release_for_epic(f"epic-{epic_id.lower()}")
        graph = backend.load()
        engine = QueryEngine(graph)
        return engine.find_release_for(f"epic-{epic_id.lower()}")
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Failed to query release for epic %s", epic_id)
        return None


def _load_ego_subgraph(
    backend: GraphTraversalBackend,
    keywords: list[str],
    depth: int = 2,
) -> tuple[Graph, list[str]]:
    """Find module seeds and return combined ego subgraph + seed IDs.

    Avoids loading the full graph — queries module node IDs directly,
    matches keywords, then calls ego_subgraph() per seed.
    """
    all_modules = backend.get_module_ids()
    seeds = [m for m in all_modules if any(kw in m.lower() for kw in keywords)]
    if not seeds:
        return Graph(), []

    combined = Graph()
    for seed_id in seeds:
        sub = backend.ego_subgraph(seed_id, depth=depth)
        for node_id, attrs in sub.graph.nodes(data=True):
            combined.graph.add_node(node_id, **cast("GraphAttrs", attrs))
        for src, tgt, key, attrs in sub.graph.edges(keys=True, data=True):
            combined.graph.add_edge(src, tgt, key=key, **attrs)
    return combined, seeds


def _resolve_graph_and_seeds(
    backend: object,
    keywords: list[str],
) -> tuple[Graph, list[str]]:
    """Return (graph, seed_ids) using the fastest path for the given backend."""
    if isinstance(backend, GraphTraversalBackend):
        return _load_ego_subgraph(backend, keywords)
    graph = cast("_SupportsGraphLoad", backend).load()
    return graph, _find_module_seeds(graph, keywords)


_TOKEN_BUDGET = 300
_TOKENS_PER_SYMBOL = 15
_MAX_SYMBOLS = _TOKEN_BUDGET // _TOKENS_PER_SYMBOL


def _derive_keywords(work: CurrentWork) -> list[str]:
    """Extract search keywords from active work context.

    Derives keywords from branch name (slug segments) and story/epic IDs.
    Returns empty list when no meaningful work context exists.
    """
    keywords: list[str] = []

    if work.branch:
        parts = (
            work.branch.replace("/", " ").replace("-", " ").replace("_", " ").split()
        )
        stop = {"story", "epic", "feature", "fix", "chore", "s", "e"}
        keywords.extend(
            p.lower() for p in parts if len(p) > 2 and p.lower() not in stop
        )

    if work.story:
        keywords.append(work.story.lower())
    if work.epic:
        keywords.append(work.epic.lower())

    return keywords


def _find_module_seeds(
    graph: Graph,
    keywords: list[str],
) -> list[str]:
    """Match keywords against module node IDs in the graph.

    Returns module IDs (e.g. ["mod-session", "mod-context"]) where
    any keyword appears as a substring of the module ID.
    """
    seeds: list[str] = []
    for node in graph.iter_concepts():
        if node.type != "module":
            continue
        node_id_lower = node.id.lower()
        if any(kw in node_id_lower for kw in keywords):
            seeds.append(node.id)
    return seeds


def get_code_symbols(
    project_path: Path,
    current_work: CurrentWork | None = None,
) -> list[GraphNode]:
    """Query graph for SymbolNodes relevant to active work using spreading activation.

    Seeds SA from module nodes matching branch/story keywords, then ranks
    symbol nodes by structural proximity. Budgets output to ~300 tokens.

    Each returned symbol has ``sa_score`` in its metadata for downstream formatting.

    Args:
        project_path: Absolute path to the project root.
        current_work: Active work context with branch/story/epic.

    Returns:
        List of SymbolNode GraphNodes sorted by SA score, limited to _MAX_SYMBOLS.
    """
    if current_work is None or not (current_work.branch or current_work.story):
        return []

    keywords = _derive_keywords(current_work)
    if not keywords:
        return []

    graph_path = project_path / GRAPH_REL_PATH

    try:
        from raise_core.graph.retrieval.engine import spreading_activation

        backend = get_active_backend(graph_path, project_root=project_path)
        graph, seeds = _resolve_graph_and_seeds(backend, keywords)

        if not seeds:
            return []

        sa_scores = spreading_activation(graph, seed_ids=seeds, decay=0.5, max_depth=2)

        scored_symbols: list[tuple[GraphNode, float]] = []
        for node in graph.iter_concepts():
            if node.type != "symbol":
                continue
            score = sa_scores.get(node.id, 0.0)
            if score > 0.0:
                scored_symbols.append((node, score))

        scored_symbols.sort(key=lambda pair: pair[1], reverse=True)

        result: list[GraphNode] = []
        for node, score in scored_symbols[:_MAX_SYMBOLS]:
            node.metadata["sa_score"] = round(score, 2)
            result.append(node)

        return result
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Code symbol query failed", exc_info=True)
        return []


@lru_cache(maxsize=1)
def _get_click_group() -> object | None:
    """Materialize the Typer app into a Click group once and cache it.

    ``typer.main.get_command(app)`` evaluates type hints for every CLI
    function — 13M+ calls taking ~8s.  Caching avoids repeating this
    for each ``get_cli_commands`` / ``get_command_detail`` invocation.
    """
    try:
        import typer

        from raise_cli.cli.main import app  # noqa: PLC0415

        return typer.main.get_command(app)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("CLI app materialization failed", exc_info=True)
        return None


def _resolve_click_command(cmd_path: list[str]) -> object | None:
    """Walk the cached Click tree to find a leaf command, or None."""
    click_group = _get_click_group()
    if click_group is None:
        return None
    current: object = click_group
    for name in cmd_path:
        cmd_map = getattr(current, "commands", {})
        if name not in cmd_map:
            return None
        current = cmd_map[name]
    return current


def get_cli_commands() -> list[str]:
    """Return a flat list of available CLI commands via Click introspection.

    Lazy-imports the CLI app to avoid circular imports at module level
    (bundle_data is imported by bundle, which is imported by cli.commands.session,
    which is imported by cli.main).

    Returns:
        Sorted list of "rai comando subcomando" strings for all leaf commands.
    """
    click_group = _get_click_group()
    if click_group is None:
        return []

    commands: list[str] = []

    def _walk(group: object, prefix: str) -> None:
        cmd_map = getattr(group, "commands", {})
        for name in sorted(cmd_map):
            cmd = cmd_map[name]
            full = f"{prefix} {name}"
            sub = getattr(cmd, "commands", {})
            if sub:
                _walk(cmd, full)
            else:
                commands.append(full)

    _walk(click_group, "rai")
    return commands


@dataclass
class CommandDetail:
    """Introspected sig and notes for a single CLI command."""

    sig: str
    notes: str


_TYPE_LABEL: dict[str, str] = {"integer": "INT", "boolean": "BOOL", "float": "FLOAT"}


def _pick_display_opt(opts: list[str]) -> str:
    """Pick which opt string represents a param in the CLI Quick Reference.

    Prefers the long form (e.g. "--project") when the command declares one —
    long flags are self-documenting for a reference table meant to be read
    by someone unfamiliar with the command, even though the short alias is
    what a fluent user would actually type. Falls back to the short alias
    only when no long form exists.
    """
    long_opts = [opt for opt in opts if opt.startswith("--")]
    if long_opts:
        return max(long_opts, key=len)
    return max(opts, key=len)


def _format_param_sig(param: object) -> str | None:
    """Format a single Click param into a human-readable sig token."""
    import click

    if "--help" in getattr(param, "opts", []):
        return None
    if isinstance(param, click.Argument):
        return param.human_readable_name.upper()
    if isinstance(param, click.Option):
        opt = _pick_display_opt(param.opts)
        if param.is_flag:
            return f"[{opt}]"
        raw = getattr(param.type, "name", "text") or "text"
        label = _TYPE_LABEL.get(raw.lower(), raw.upper())
        return f"{opt} {label}" if param.required else f"[{opt} {label}]"
    return None


def _detail_from_command(current: object) -> CommandDetail:
    """Build a CommandDetail from an already-resolved Click command.

    Notes prefer the command's curated `short_help` — the same field Click
    already exposes for one-line summaries — when a command explicitly sets
    one. That is the single source of truth for curated notes: it lives in
    the command decorator, not in a parallel copy. Commands without a
    curated `short_help` fall back to the first line of the full `help`
    text (prior behavior), so uncurated commands still get a usable note.
    """
    parts = [
        tok
        for p in getattr(current, "params", [])
        if (tok := _format_param_sig(p)) is not None
    ]
    raw_help: str = getattr(current, "help", "") or ""
    short_help: str = getattr(current, "short_help", "") or ""
    notes = short_help.strip() if short_help else raw_help.split("\n")[0].strip()
    return CommandDetail(sig=" ".join(parts), notes=notes)


def get_command_detail(cmd_path: list[str]) -> CommandDetail:
    """Return sig and notes for a CLI command via Click introspection.

    Args:
        cmd_path: Command name tokens after "rai" (e.g. ["session", "start"]).

    Returns:
        CommandDetail(sig, notes). Returns empty strings on any failure or if
        the command is not found.
    """
    _empty = CommandDetail(sig="", notes="")
    try:
        current = _resolve_click_command(cmd_path)
        if current is None:
            return _empty
        return _detail_from_command(current)

    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("get_command_detail failed for %s", cmd_path, exc_info=True)
        return _empty
