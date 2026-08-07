"""Unified graph builder for context integration.

This module provides the GraphBuilder class that merges memory, work,
skills, and cartridge-extracted governance into a single Graph for
context queries. Governance extraction uses the cartridge pipeline
(ADR-089) — the legacy GovernanceExtractor was removed in S10328.7.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from raise_cli.config.agents import AgentConfig, get_agent_config
from raise_cli.context.extractors.relationships import (
    GraphHealthReport,
    infer_relationships,
)
from raise_cli.context.extractors.skills import extract_all_skills
from raise_cli.context.extractors.structure import (
    extract_bounded_contexts,
    extract_constraints,
    extract_layers,
)
from raise_cli.context.loaders.architecture import (
    load_architecture as _load_architecture,
)
from raise_cli.context.loaders.components import load_components as _load_components
from raise_cli.context.loaders.documents import (
    load_document_chunks as _load_document_chunks,
)
from raise_cli.context.loaders.identity import load_identity as _load_identity
from raise_cli.context.loaders.memory import load_memory as _load_memory
from raise_cli.context.loaders.work import load_sessions as _load_sessions
from raise_cli.context.loaders.work import load_stories as _load_stories
from raise_cli.portfolio.component_map import resolve_component
from raise_core.cartridges.ingest import (
    ingest_cartridge,
    is_snapshot_cartridge,
    materialize_cross_cartridge_edges,
)
from raise_core.cartridges.repo import generate_repo_cartridge
from raise_core.discovery.symbols import IngestReport, SymbolDepth
from raise_core.discovery.symbols import load_symbols as _load_symbols
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode

if TYPE_CHECKING:
    from raise_cli.context.analyzers.models import ModuleInfo
    from raise_cli.onboarding.manifest import ProjectManifest

logger = logging.getLogger(__name__)

#: Advisory emitted when nothing configures the documents loader (RAISE-15992).
#: ``graph.document_sources`` is opt-in, so the out-of-the-box experience was a
#: graph that silently knew nothing about the project's own prose. Naming the
#: key, the file and the guide turns "the graph is useless for my docs" into a
#: one-line edit.
NO_DOCUMENT_SOURCES_HINT = (
    "No documents indexed: 'graph.document_sources' is unset in "
    ".raise/manifest.yaml. Add globs (e.g. 'dev/sops/*.md', "
    "'work/epics/*/scope.md') to index your docs — "
    "see docs/concepts/knowledge-graph.md ('Indexing Documents')."
)


class GraphBuilder:
    """Builds unified context graph from all sources.

    Merges governance documents, memory JSONL files, work tracking,
    and skill metadata into a single queryable graph.

    Attributes:
        project_root: Root directory for the project.

    Examples:
        >>> builder = GraphBuilder(Path("."))
        >>> graph = builder.build()
        >>> graph.node_count
        50
    """

    def __init__(
        self,
        project_root: Path | None = None,
        *,
        agent_config: AgentConfig | None = None,
        strict: bool = False,
        symbol_depth: SymbolDepth = SymbolDepth.FULL,
    ) -> None:
        """Initialize builder with project root.

        Args:
            project_root: Root directory for the project. Defaults to cwd.
            agent_config: Agent configuration. Defaults to Claude.
            strict: If True, raise ValueError on duplicate node IDs.
                If False (default), warn and skip duplicates (RAISE-648).
            symbol_depth: Which symbol kinds to include in graph.
        """
        self.project_root = project_root or Path.cwd()
        self.ide_config = agent_config or get_agent_config()
        self.strict = strict
        self.symbol_depth = symbol_depth
        self.warnings: list[str] = []
        # Advisory notes about configuration, kept apart from `warnings`
        # (RAISE-15992): a warning means the build dropped data and is counted
        # as such by the graph_update hook, while a hint means the build did
        # exactly what it was told and the operator may not have meant it.
        self.hints: list[str] = []
        self.symbol_ingest_report: IngestReport = IngestReport()
        self.health_report: GraphHealthReport = GraphHealthReport(
            total_nodes=0, total_edges=0
        )

    def build(self) -> Graph:
        """Build unified graph from all sources.

        Loads concepts from governance, memory, work, skills, and components,
        then builds a Graph with all nodes. After all nodes are loaded,
        extracts structural nodes (bounded contexts, layers) and their edges.

        Returns:
            Graph containing all concepts.
        """
        graph = Graph()

        # Load all sources
        all_nodes: list[GraphNode] = []
        all_nodes.extend(self.load_memory())
        all_nodes.extend(self.load_sessions())
        all_nodes.extend(self.load_stories())
        all_nodes.extend(self.load_skills())
        all_nodes.extend(self.load_components())
        all_nodes.extend(self.load_architecture())
        all_nodes.extend(self.load_identity())
        all_nodes.extend(self.load_documents())

        # Load cartridge nodes + edges (ADR-089 D1 — S6589.6a)
        cartridge_nodes, cartridge_edges = self.load_cartridges()
        all_nodes.extend(cartridge_nodes)

        # Ingest public code symbols as SymbolNode + typed edges (S2162.1).
        # Runs after load_components so module nodes exist for edge safety.
        symbol_nodes, symbol_edges, ingest_report = _load_symbols(
            self.project_root, depth=self.symbol_depth
        )
        self.symbol_ingest_report = ingest_report
        all_nodes.extend(symbol_nodes)

        # Enrich module nodes with real code analysis (S16.1)
        # Must run before add_concept() so graph gets enriched copies
        self.load_code_structure(all_nodes)

        # Detect duplicate node IDs (RAISE-648: warn+skip by default, raise with --strict)
        seen_ids: dict[str, str] = {}
        unique_nodes: list[GraphNode] = []
        for node in all_nodes:
            if node.id in seen_ids:
                msg = (
                    f"Duplicate node ID '{node.id}' — "
                    f"'{node.source_file or 'unknown'}' skipped, "
                    f"keeping '{seen_ids[node.id]}'"
                )
                if self.strict:
                    raise ValueError(msg)
                logger.warning(msg)
                self.warnings.append(msg)
                continue
            seen_ids[node.id] = node.source_file or "unknown"
            unique_nodes.append(node)

        # Add nodes to graph
        for node in unique_nodes:
            graph.add_concept(node)

        # Extract structural nodes and edges (E15 — bounded contexts, layers)
        # Runs after all nodes loaded so module nodes exist for edge safety
        node_by_id: dict[str, GraphNode] = {n.id: n for n in all_nodes}
        structural_nodes: list[GraphNode] = []
        structural_edges: list[GraphEdge] = []

        bc_nodes, bc_edges = extract_bounded_contexts(all_nodes, node_by_id)
        structural_nodes.extend(bc_nodes)
        structural_edges.extend(bc_edges)

        lyr_nodes, lyr_edges = extract_layers(all_nodes, node_by_id)
        structural_nodes.extend(lyr_nodes)
        structural_edges.extend(lyr_edges)

        for node in structural_nodes:
            graph.add_concept(node)
        all_nodes.extend(structural_nodes)

        # Update node_by_id with structural nodes for constraint edge safety
        node_by_id.update({n.id: n for n in structural_nodes})

        # Extract constraint edges (S15.3 — guardrail → BC/layer)
        constraint_edges = extract_constraints(all_nodes, node_by_id)
        structural_edges.extend(constraint_edges)

        # Symbol-level edges (implements_symbol / calls / inherits_from).
        # Filter against node_by_id to drop edges whose module target was
        # inferred heuristically but has no real ModuleNode (ADR-E2162-1):
        # the loader derives `mod-<dir>` from the file path, which produces
        # dangling ids for directories without governance/architecture YAMLs.
        safe_symbol_edges = [
            e for e in symbol_edges if e.source in node_by_id and e.target in node_by_id
        ]
        structural_edges.extend(safe_symbol_edges)

        # Cartridge edges (ADR-089 D2 — S6589.6a) — filter for node safety
        safe_cartridge_edges = [
            e
            for e in cartridge_edges
            if e.source in node_by_id and e.target in node_by_id
        ]
        structural_edges.extend(safe_cartridge_edges)

        # Infer and add relationships
        inferred_edges, health_report = infer_relationships(all_nodes)
        for edge in inferred_edges:
            graph.add_relationship(edge)

        # Add structural edges (explicit, not inferred)
        for edge in structural_edges:
            graph.add_relationship(edge)

        # Generate repo cartridge if .raise/cartridges/ exists
        cartridges_dir = self.project_root / ".raise" / "cartridges"
        if cartridges_dir.is_dir():
            generate_repo_cartridge(graph, cartridges_dir)

        # Populate post-build observability field on the ingest report.
        self.symbol_ingest_report.total_nodes_after = graph.node_count

        # Store health report with final counts (includes structural edges).
        health_report.total_nodes = graph.node_count
        health_report.total_edges = graph.edge_count
        self.health_report = health_report

        return graph

    def load_memory(self) -> list[GraphNode]:
        """Load concepts from memory JSONL files across all tiers.

        Delegates to loaders.memory.load_memory().
        """
        return _load_memory(self.project_root)

    def load_sessions(self) -> list[GraphNode]:
        """Load SessionNode instances from the sessions table in raise.db.

        Projects each session row into a SessionNode so that patterns with
        ``learned_from`` references to session ids can resolve (RAISE-15988).

        Delegates to loaders.work.load_sessions().
        """
        return _load_sessions(self.project_root)

    def load_stories(self) -> list[GraphNode]:
        """Load StoryNode instances from the story_stats table in raise.db.

        Projects each story row with an S/F-format id into a StoryNode so that
        patterns with ``learned_from`` references to story ids can resolve
        (RAISE-15988).

        Delegates to loaders.work.load_stories().
        """
        return _load_stories(self.project_root)

    def load_skills(self) -> list[GraphNode]:
        """Load concepts from skill YAML frontmatter.

        Parses SKILL.md files in the IDE's skill directory.

        Returns:
            List of GraphNode for skill concepts.
        """
        raw_skills_dir = self.ide_config.skills_dir or ".claude/skills"
        skills_dir = self.project_root / raw_skills_dir
        return extract_all_skills(skills_dir)

    def load_components(self) -> list[GraphNode]:
        """Load discovered components from validated JSON.

        Delegates to loaders.components.load_components().
        """
        return _load_components(self.project_root)

    def load_architecture(self) -> list[GraphNode]:
        """Load architecture nodes from documentation.

        Delegates to loaders.architecture.load_architecture().
        """
        return _load_architecture(self.project_root)

    def load_identity(self) -> list[GraphNode]:
        """Load Rai identity values and boundaries from core.yaml.

        Delegates to loaders.identity.load_identity().
        """
        return _load_identity(self.project_root)

    def load_documents(self) -> list[GraphNode]:
        """Load freeform documents (SOPs, RFCs, research) from manifest-configured globs.

        Reads ``graph.document_sources`` from manifest.yaml. No-op if absent —
        but a recorded no-op: both "never configured" and "configured, matched
        nothing" append to :attr:`hints` so zero document nodes is never a
        silent outcome (RAISE-15992).

        Loads one node per document **section**, not per file (RAISE-15990):
        a whole document as a single node is diluted by the length
        normalization in the scorers, so retrieval could not reach the
        section a query was actually about. ``rai docs migrate`` keeps using
        the file-level ``load_documents`` loader, which is why the two live
        behind separate entry points.
        """
        from raise_cli.onboarding.manifest import load_manifest

        manifest = load_manifest(self.project_root)
        sources = (
            manifest.graph.document_sources
            if manifest is not None and manifest.graph is not None
            else []
        )
        if not sources:
            self.hints.append(NO_DOCUMENT_SOURCES_HINT)
            return []

        # Per-pattern, not aggregate: with nine working globs the tenth can rot
        # after a directory rename and an aggregate check would stay silent.
        dead = [
            p
            for p in sources
            if not any(m.is_file() for m in self.project_root.glob(p))
        ]
        if dead:
            self.hints.append(
                "'graph.document_sources' patterns matched no files: "
                f"{', '.join(dead)}. Patterns in .raise/manifest.yaml are "
                "globs relative to the project root."
            )
        return _load_document_chunks(self.project_root, sources)

    def load_cartridges(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Load cartridge nodes and edges from all cartridge roots.

        Scans both ``.raise/cartridges/`` (repo-local) and
        ``$RAI_HOME/cartridges/`` (external — RAISE-13911 DD-2 (b), the
        memory cartridge lives outside the repo so a derived index over
        personal memory is structurally impossible to commit). Iterates
        each cartridge subdirectory in both roots, calls ingest_cartridge()
        (which handles manifest parsing, node loading, and edge
        materialization), then runs a cross-cartridge reference pass
        (DA-5) on the unified node set to detect name mentions across
        cartridge boundaries.

        Returns:
            Tuple of (nodes, edges) from all discovered cartridges,
            including cross-cartridge reference edges.
        """
        from raise_cli.config.paths import get_external_cartridge_roots

        all_nodes: list[GraphNode] = []
        all_edges: list[GraphEdge] = []
        for cartridges_dir in get_external_cartridge_roots(self.project_root):
            if not cartridges_dir.is_dir():
                continue
            for entry in sorted(cartridges_dir.iterdir()):
                if not entry.is_dir():
                    continue
                if is_snapshot_cartridge(entry):
                    # RAISE-13378 Option A: this cartridge is a snapshot of the
                    # build graph itself (e.g. repo) — re-ingesting it would feed
                    # stale, relabeled nodes back into the next build.
                    continue
                try:
                    graph = ingest_cartridge(entry)
                    all_nodes.extend(graph.iter_concepts())
                    all_edges.extend(graph.iter_relationships())
                except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                    logger.warning("Failed to ingest cartridge %s", entry.name)

        # DA-5: cross-cartridge reference edges — detect name mentions
        # across cartridge boundaries on the unified node set.
        if len(all_nodes) > 1:
            unified = Graph()
            for node in all_nodes:
                unified.add_concept(node)
            cross_count = materialize_cross_cartridge_edges(unified)
            if cross_count:
                all_edges.extend(unified.iter_relationships())
                logger.info(
                    "Materialized %d cross-cartridge reference edges", cross_count
                )

        return all_nodes, all_edges

    def load_code_structure(self, all_nodes: list[GraphNode]) -> None:
        """Enrich module nodes with real code analysis data.

        Reads package paths from the manifest (project.apps[].path) to
        support monorepo layouts. Falls back to root-level src/ for
        single-package projects.

        Args:
            all_nodes: All nodes loaded so far (mutated in place).
        """
        from raise_cli.onboarding.manifest import load_manifest

        manifest = load_manifest(self.project_root)

        # Apply portfolio component tags BEFORE the early-return guard so they
        # are populated even when no src roots yield code modules (RAISE-15251).
        component_paths: dict[str, list[str]] = (
            manifest.project.portfolio.component_paths
            if manifest and manifest.project.portfolio
            else {}
        )
        self.apply_portfolio_tags(all_nodes, component_paths)

        if component_paths:
            from raise_cli.portfolio.storage import PortfolioStore  # noqa: PLC0415

            n = PortfolioStore(self.project_root).sync_manifest_catalog(component_paths)
            if n:
                import logging  # noqa: PLC0415

                logging.getLogger(__name__).debug(
                    "portfolio_components: %d componentes sincronizados desde manifest",
                    n,
                )

        src_roots = self._resolve_src_roots(manifest)
        code_modules = self._scan_src_roots(src_roots)

        if not code_modules:
            return

        code_by_name: dict[str, ModuleInfo] = {m.name: m for m in code_modules}
        self._apply_code_enrichment(all_nodes, code_by_name)

    def _scan_src_roots(self, src_roots: list[str]) -> list[ModuleInfo]:
        """Scan src roots for Python and TypeScript packages."""
        from raise_cli.context.analyzers.python import PythonAnalyzer
        from raise_cli.context.analyzers.typescript import TypeScriptAnalyzer

        code_modules: list[ModuleInfo] = []
        for src_root in src_roots:
            src_path = self.project_root / src_root
            if not src_path.is_dir():
                continue
            for pkg_dir in sorted(src_path.iterdir()):
                if not pkg_dir.is_dir() or pkg_dir.name.startswith("__"):
                    continue
                if (pkg_dir / "__init__.py").exists():
                    rel = str(pkg_dir.relative_to(self.project_root))
                    analyzer = PythonAnalyzer(src_dir=rel)
                    if analyzer.detect(self.project_root):
                        code_modules.extend(analyzer.analyze_modules(self.project_root))
                elif (pkg_dir / "package.json").exists() or (
                    pkg_dir / "tsconfig.json"
                ).exists():
                    rel = str(pkg_dir.relative_to(self.project_root))
                    analyzer_ts = TypeScriptAnalyzer(src_dir=rel)
                    if analyzer_ts.detect(self.project_root):
                        code_modules.extend(
                            analyzer_ts.analyze_modules(self.project_root)
                        )
        return code_modules

    @staticmethod
    def _apply_code_enrichment(
        all_nodes: list[GraphNode],
        code_by_name: dict[str, ModuleInfo],
    ) -> None:
        """Merge code analysis into module nodes and append content summary."""
        for node in all_nodes:
            if node.type != "module":
                continue

            mod_name = node.id.removeprefix("mod-")
            info = code_by_name.get(mod_name)
            if info is None:
                continue

            node.metadata["code_imports"] = info.imports
            node.metadata["code_exports"] = info.exports
            node.metadata["code_components"] = info.component_count

            parts = []
            if info.exports:
                parts.append(f"{len(info.exports)} exports")
            if info.imports:
                parts.append(f"{len(info.imports)} imports")
            parts.append(f"{info.component_count} components")
            node.content = f"{node.content}\n\nCode: {', '.join(parts)}"

    def apply_portfolio_tags(
        self,
        all_nodes: list[GraphNode],
        component_paths: dict[str, list[str]],
    ) -> None:
        """Tag SymbolNodes and module nodes with portfolio component identifiers.

        For each SymbolNode whose ``metadata["file"]`` matches a prefix in
        ``component_paths``, sets ``metadata["portfolio_component"]`` to the
        matched component name.  The owning module node (identified by
        ``metadata["module"]``) also receives ``metadata["portfolio_components"]``
        — a sorted list of all components touched by its symbols.

        A WARNING is logged for each component whose prefixes matched 0 nodes
        so misconfigurations in the manifest surface at build time (non-fatal).

        Args:
            all_nodes: All nodes collected so far (mutated in place).
            component_paths: Mapping of component name → path prefix list from
                ``project.portfolio.component_paths`` in the manifest.
        """
        if not component_paths:
            return

        # Track which module ids belong to which components (for module tagging)
        module_components: dict[str, set[str]] = {}
        # Track whether each component matched at least one node
        zero_match: dict[str, bool] = dict.fromkeys(component_paths, False)

        # Build a lookup so module nodes can be retrieved by id
        node_by_id: dict[str, GraphNode] = {n.id: n for n in all_nodes}

        for node in all_nodes:
            if node.type != "symbol":
                continue
            file_path: str = node.metadata.get("file", "")
            if not file_path:
                continue
            component = resolve_component(file_path, component_paths)
            if component is not None:
                node.metadata["portfolio_component"] = component
                zero_match[component] = True
                mod_id: str = node.metadata.get("module", "")
                if mod_id:
                    module_components.setdefault(mod_id, set()).add(component)

        # Propagate sorted component sets to module nodes
        for mod_id, components in module_components.items():
            if mod_id in node_by_id:
                node_by_id[mod_id].metadata["portfolio_components"] = sorted(components)

        self._warn_unmatched_components(zero_match)

    @staticmethod
    def _warn_unmatched_components(zero_match: dict[str, bool]) -> None:
        """Emit a WARNING for each component that matched 0 SymbolNodes."""
        for component, matched in zero_match.items():
            if not matched:
                logger.warning(
                    "portfolio: component %r matched 0 nodes — check component_paths in manifest",
                    component,
                )

    @staticmethod
    def _resolve_src_roots(
        manifest: ProjectManifest | None,
    ) -> list[str]:
        """Derive src/ directories from manifest apps or fall back to root."""
        if manifest and manifest.project and manifest.project.apps:
            return [f"{app.path}/src" for app in manifest.project.apps]
        return ["src"]

    def infer_relationships(
        self, nodes: list[GraphNode]
    ) -> tuple[list[GraphEdge], GraphHealthReport]:
        """Infer relationships between concepts.

        Delegates to extractors.relationships module.
        """
        return infer_relationships(nodes)
