"""Instructions file generation for project onboarding.

Generates project-specific instructions content (AGENTS.md, .cursor/rules/raise.mdc,
.windsurf/rules/raise.md, etc.) from .raise/ canonical sources.  A .raise/ directory
must exist before generation — ``rai init`` always creates it first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.config.agents import AgentConfig
from raise_cli.onboarding.conventions import ConventionResult
from raise_cli.onboarding.detection import DetectionResult

_CLI_COMMANDS_YAML_PATH = Path(__file__).parent / "cli_commands.yaml"


def _load_cli_sections(yaml_path: Path) -> list[dict[str, Any]]:
    """Parse cli_commands.yaml and return the sections list with type guarantees."""
    try:
        raw: Any = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return []
        typed: dict[str, Any] = cast("dict[str, Any]", raw)
        sections: Any = typed.get("sections", [])
        if not isinstance(sections, list):
            return []
        return cast("list[dict[str, Any]]", sections)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return []


def _str_from_nested(data: dict[str, Any], key1: str, key2: str) -> str | None:
    """Safely extract a string from a nested dict (YAML-loaded data).

    Works with YAML-loaded dicts which have ``Any``-typed values.
    """
    outer = data.get(key1)
    if not isinstance(outer, dict):
        return None
    typed: dict[str, object] = {str(k): v for k, v in outer.items()}  # type: ignore[union-attr]
    raw = typed.get(key2)
    return raw if isinstance(raw, str) else None


class InstructionsGenerator:
    """Generates agent instructions file content from .raise/ sources.

    Reads identity, methodology, manifest, and optional integration configs
    to produce a comprehensive instructions file (e.g. AGENTS.md).
    """

    def generate(
        self,
        project_name: str,
        detection: DetectionResult,
        conventions: ConventionResult | None = None,
        *,
        project_path: Path,
    ) -> str:
        """Generate AGENTS.md content from .raise/ canonical sources.

        Args:
            project_name: Name of the project.
            detection: Project detection result (type, file count).
            conventions: Optional convention detection result (unused, kept
                for backward compatibility).
            project_path: Project root path containing .raise/ directory.

        Returns:
            Markdown content for AGENTS.md.
        """
        raise_dir = project_path / ".raise"
        return self._generate_raise_project(project_name, raise_dir)

    # =========================================================================
    # RaiSE Project Generation
    # =========================================================================

    def _generate_raise_project(
        self,
        project_name: str,
        raise_dir: Path,
    ) -> str:
        """Generate AGENTS.md for a RaiSE project from .raise/ sources.

        Reads identity, methodology, manifest, and optional integration
        configs to produce a comprehensive AGENTS.md.
        """
        lines: list[str] = []

        # Header comment
        lines.append(
            "<!-- Generated from .raise/ canonical source. "
            "Do not edit manually. Regenerate with: rai init -->"
        )
        lines.append("")

        # Project title + session start
        lines.append("# RaiSE Project")
        lines.append("")
        lines.append(
            "Run `/rai-session-start` at the beginning of each session "
            "to load full context (patterns, coaching, session continuity)."
        )
        lines.append("")

        # Graph Access Patterns (RAISE-16743) — before Identity, highest visibility
        self._add_graph_access_section(lines)

        # Load sources
        identity_path = raise_dir / "rai" / "identity" / "core.yaml"
        methodology_path = raise_dir / "rai" / "framework" / "methodology.yaml"
        manifest_path = raise_dir / "manifest.yaml"
        backlog_config_path = raise_dir / "backlog.yaml"
        legacy_jira_path = raise_dir / "jira.yaml"

        methodology: dict[str, Any] = {}
        if methodology_path.is_file():
            methodology = (
                yaml.safe_load(methodology_path.read_text(encoding="utf-8")) or {}
            )

        manifest: dict[str, Any] = {}
        if manifest_path.is_file():
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}

        dev_branch = _str_from_nested(manifest, "branches", "development") or "dev"

        # Identity section
        if identity_path.is_file():
            try:
                identity_data: Any = yaml.safe_load(
                    identity_path.read_text(encoding="utf-8")
                )
            except yaml.YAMLError:
                identity_data = None
            if isinstance(identity_data, dict):
                self._add_identity_section_from_yaml(
                    lines, cast("dict[str, Any]", identity_data)
                )

        # Process Rules section
        if methodology:
            self._add_process_rules_section(lines, methodology)

        # Branch Model section
        if methodology.get("branches"):
            self._add_branch_model_section(lines, methodology, dev_branch)

        # CLI Quick Reference (static content)
        self._add_cli_reference_section(lines)

        # External Integrations (only if a backlog config exists).
        # Gated on either file, never on jira.yaml alone: that gate cost a
        # correctly migrated project the MCP and docs lines too (RAISE-16994).
        if backlog_config_path.is_file() or legacy_jira_path.is_file():
            self._add_integrations_section(
                lines, legacy_jira_present=legacy_jira_path.is_file()
            )

        # File Operations (static)
        self._add_file_operations_section(lines)

        # Post-Compaction (static)
        self._add_post_compaction_section(lines)

        return "\n".join(lines)

    def _add_graph_access_section(self, lines: list[str]) -> None:
        """Add Graph Access Patterns section (RAISE-16743, static content).

        Placed before Identity for highest visibility — reading this project
        starts with the graph, not a search. It's the default first move for
        anything about this project (code, backlog, docs alike); the live
        backlog adapter (Jira, etc.) is the exception, reserved for
        writes/mutations or genuinely missing data — not a parallel tip
        presented alongside grepping.
        """
        lines.append("## Graph Access Patterns")
        lines.append("")
        lines.append(
            "Reading this project starts with the graph, not a search. Query it "
            "before grepping and before calling a live backlog adapter — it "
            "already holds this project's code, backlog items, and docs, "
            "answers offline, and returns in one call what would otherwise "
            "take many file reads or an API round-trip."
        )
        lines.append("")
        lines.append("### Backlog lookup — the graph, not a live Jira call")
        lines.append('    rai graph query "RAISE-1234" --types backlog.story')
        lines.append("")
        lines.append("### Code or docs by keyword")
        lines.append('    rai graph query "session lifecycle"')
        lines.append("")
        lines.append("### Full context for a module")
        lines.append("    rai graph context mod-session")
        lines.append("")
        lines.append("### Filtering results by metadata")
        lines.append(
            '    rai graph query "RAISE" --filter "priority:Major" --types backlog'
        )
        lines.append("")
        lines.append(
            "Operators: `:` (eq), `!=` (neq), `>`, `>=`, `<`, `<=`, `~` (contains). "
            "Comma in value = `in`. Multiple `--filter` flags combine with AND."
        )
        lines.append(
            "Discover available fields: `rai graph fields --type backlog.story`"
        )
        lines.append("")
        lines.append(
            "**Note:** `neq` on an absent field returns false (not true). "
            "Filters reflect the last `rai graph build`, not live Jira."
        )
        lines.append("")
        lines.append(
            "Filter-only (no keyword): `--filter` works without a query string."
        )
        lines.append('    rai graph query --filter "key:RAISE-1234" --types backlog')
        lines.append("")
        lines.append(
            "Depth expansion: `--depth N` expands graph edges (child_of, depends_on) "
            "per result. Requires edges materialized by `rai graph build`."
        )
        lines.append(
            '    rai graph query --filter "key:RAISE-1234" --types backlog --depth 1'
        )
        lines.append("")
        lines.append("If the graph returns empty, run `rai graph build` to refresh it.")
        lines.append("")
        lines.append(
            "The live adapter is the exception: reach for it only to write "
            "or transition something, or when what's needed genuinely isn't "
            "in the graph yet."
        )
        lines.append("Build/refresh with: rai graph build")
        lines.append("")

    def _add_identity_section_from_yaml(
        self, lines: list[str], data: dict[str, Any]
    ) -> None:
        """Add Rai Identity section from structured core.yaml data."""
        lines.append("## Rai Identity")
        lines.append("")

        # Values
        values: list[dict[str, Any]] = data.get("values", [])
        if values:
            lines.append("### Values")
            for v in values:
                name: str = v.get("name", "")
                desc: str = v.get("description", "")
                lines.append(f"{v.get('number', '?')}. {name} — {desc}")
            lines.append("")

        # Boundaries
        boundaries: dict[str, Any] = data.get("boundaries", {})
        will_items: list[str] = boundaries.get("will", [])
        wont_items: list[str] = boundaries.get("wont", [])
        if will_items or wont_items:
            lines.append("### Boundaries")
            if will_items:
                lines.append("I Will: " + ", ".join(will_items))
            if wont_items:
                lines.append("I Won't: " + ", ".join(wont_items))
            lines.append("")

        # Principles
        principles: list[dict[str, str]] = data.get("principles", [])
        if principles:
            lines.append("### Principles")
            for i, p in enumerate(principles, 1):
                lines.append(f"{i}. {p.get('name', '')} — {p.get('embodiment', '')}")
            lines.append("")

    def _add_process_rules_section(  # noqa: C901 -- complexity 15, refactor deferred
        self, lines: list[str], methodology: dict[str, Any]
    ) -> None:
        """Add Process Rules section from methodology.yaml."""
        lines.append("## Process Rules")
        lines.append("")

        # Work Lifecycle
        lifecycle = methodology.get("lifecycle", {})
        if lifecycle:
            lines.append("### Work Lifecycle")
            for work_type in ["epic", "story", "session"]:
                cfg = lifecycle.get(work_type, {})
                flow = cfg.get("flow", "")
                if flow:
                    lines.append(f"{work_type.upper()}: {flow}")
            lines.append("")

        # Gates
        gates = methodology.get("gates", {})
        blocking = gates.get("blocking", [])
        quality = gates.get("quality", [])
        if blocking or quality:
            lines.append("### Gates")
            for gate in blocking:
                require = gate.get("require", "")
                before = gate.get("before", "")
                if require and before:
                    lines.append(f"- {require} before {before.lower()}")
            for gate in quality:
                gate_name = gate.get("gate", "")
                when = gate.get("when", "")
                if gate_name:
                    desc = f"- {gate_name}"
                    if when:
                        when_lower = when[0].lower() + when[1:] if when else when
                        desc += f" {when_lower}"
                    lines.append(desc)
            lines.append("")

        # Critical Rules from principles
        principles = methodology.get("principles", {})
        if principles:
            lines.append("### Critical Rules")
            for category in ["process", "collaboration", "technical"]:
                category_principles = principles.get(category, [])
                for p in category_principles:
                    name = p.get("name", "")
                    rule = p.get("rule", "")
                    rationale = p.get("rationale", "")
                    if name and rule:
                        line = f"- {name} \u2014 {rule}"
                        if rationale:
                            line += f" ({rationale.rstrip('.')})"
                        lines.append(line)
            lines.append("")

    def _add_branch_model_section(
        self,
        lines: list[str],
        methodology: dict[str, Any],
        dev_branch: str,
    ) -> None:
        """Add Branch Model section."""
        lines.append("## Branch Model")

        branches = methodology.get("branches", {})
        flow_items = branches.get("flow", [])

        # Build the one-liner: main (stable) -> dev (development) -> story/...
        lines.append(
            f"main (stable) \u2192 {dev_branch} (development) "
            "\u2192 story/s{N}.{M}/{name}"
        )

        # Flow description
        for flow_item in flow_items:
            resolved = flow_item.replace("{development_branch}", dev_branch)
            lines.append(resolved)
        lines.append("")

    def _add_cli_reference_section(self, lines: list[str]) -> None:
        """Add CLI Quick Reference section from cli_commands.yaml + Click introspection."""
        from raise_cli.session.bundle_data import get_command_detail

        sections = _load_cli_sections(_CLI_COMMANDS_YAML_PATH)

        lines.append("## CLI Quick Reference")
        lines.append("")

        for section in sections:
            section_name: str = section.get("name", "")
            raw_cmds: Any = section.get("commands", [])
            commands: list[str] = (
                cast("list[str]", raw_cmds) if isinstance(raw_cmds, list) else []
            )
            lines.append(f"### {section_name}")
            for cmd_full in commands:
                cmd_tokens: list[str] = str(cmd_full).removeprefix("rai ").split()
                detail = get_command_detail(cmd_tokens)
                entry = f"- cmd: {cmd_full}"
                if detail.sig:
                    entry += f" | sig: {detail.sig}"
                if detail.notes:
                    entry += f" | notes: {detail.notes}"
                lines.append(entry)
            lines.append("")

        lines.append("### Common Mistakes")
        lines.append(
            "- wrong: rai graph build --project . | right: rai graph build "
            "| why: no --project flag"
        )
        lines.append(
            '- wrong: rai pattern add --content "..." | right: rai pattern add "..." '
            "| why: CONTENT positional"
        )
        lines.append(
            "- wrong: rai pattern add --source F1 | right: --from F1 "
            "| why: flag is --from"
        )
        lines.append(
            "- wrong: rai discover scan --input dir | right: rai discover scan dir "
            "| why: PATH positional"
        )
        lines.append(
            '- wrong: rai backlog create MY_PROJECT --summary "Title" '
            '| right: rai backlog create "Title" -p MY_PROJECT '
            "| why: SUMMARY positional, project is -p flag"
        )
        lines.append(
            "- wrong: rai backlog link X Y --type blocks "
            "| right: rai backlog link X Y blocks "
            "| why: LINK_TYPE positional"
        )
        lines.append(
            '- wrong: rai backlog update KEY --field summary="X" '
            '| right: rai backlog update KEY -s "X" '
            "| why: use named flags for known fields (-s, -l, --priority, --assignee); "
            "-F is for custom fields (e.g. -F customfield_13267=Interface)"
        )
        lines.append("")

    def _add_integrations_section(
        self, lines: list[str], *, legacy_jira_present: bool = False
    ) -> None:
        """Add External Integrations section.

        Names ``.raise/backlog.yaml`` \u2014 the canonical backlog adapter config.
        The previous wording named ``.raise/jira.yaml`` and advertised
        "transition IDs": the file is deprecated and auto-migrated, and the
        transition-id namespace (``lifecycle_mapping``) is obsolete and
        removed by RAISE-16983. Both claims were false (RAISE-16994).
        """
        lines.append("## External Integrations")
        lines.append(
            "- Backlog config: `.raise/backlog.yaml` \u2014 organizations, "
            "projects, workflow states, custom fields. Read just-in-time via "
            "`rai backlog` CLI."
        )
        if legacy_jira_present:
            lines.append(
                "- `.raise/jira.yaml` is deprecated \u2014 auto-migrated into "
                "`.raise/backlog.yaml`; delete it once you have confirmed the "
                "migration."
            )
        lines.append(
            "- MCP servers: `.raise/mcp/*.yaml` \u2014 managed via "
            "`rai mcp install|scaffold|list|health`."
        )
        lines.append(
            "- Documentation targets: configured per adapter. "
            "Use `rai docs publish|get|search`."
        )
        lines.append("")

    def _add_file_operations_section(self, lines: list[str]) -> None:
        """Add File Operations section (static content)."""
        lines.append("## File Operations")
        lines.append("- ALWAYS read files explicitly before editing them")
        lines.append("- Use read tool first, then edit/write tools")
        lines.append("- Never assume file context is loaded from previous turns")
        lines.append("- After `/clear`, re-read all files you need to modify")
        lines.append("")

    def _add_post_compaction_section(self, lines: list[str]) -> None:
        """Add Post-Compaction Context Restoration section (static content)."""
        lines.append("## Post-Compaction Context Restoration")
        lines.append(
            "When you detect context was compacted "
            "(continuation summary present), restore working state:"
        )
        lines.append(
            "1. Read the session journal: "
            "`uv run rai session journal show --compact --project .`"
        )
        lines.append(
            "2. Read the current epic/story scope doc if referenced in journal"
        )
        lines.append("3. Summarize: where we are, what was decided, what's next")
        lines.append(
            "4. Continue work \u2014 do NOT re-run "
            "`/rai-session-start` (session is already active)"
        )
        lines.append("")
        lines.append(
            "The PreCompact hook logs journal state "
            "before compaction (side-effect only)."
        )
        lines.append(
            "Post-compaction injection via hooks is broken "
            "(Claude Code bugs #12671, #15174)."
        )
        lines.append("")


def generate_instructions(
    project_name: str,
    detection: DetectionResult,
    conventions: ConventionResult | None = None,
    *,
    agent_config: AgentConfig | None = None,  # noqa: ARG001 -- reserved for future agent-specific instructions
    project_path: Path,
) -> str:
    """Convenience function to generate agent instructions file content.

    Args:
        project_name: Name of the project.
        detection: Project detection result.
        conventions: Optional convention detection result (unused, kept
            for backward compatibility).
        agent_config: Agent configuration (unused, kept for backward
            compatibility).
        project_path: Project root path containing .raise/ directory.

    Returns:
        Markdown content for the agent's instructions file.

    Example:
        >>> detection = detect_project_type(Path("/my/project"))
        >>> content = generate_instructions("my-api", detection, project_path=Path("/my/project"))
        >>> Path("AGENTS.md").write_text(content)
    """
    generator = InstructionsGenerator()
    return generator.generate(
        project_name, detection, conventions, project_path=project_path
    )


# Backward-compat alias
ClaudeMdGenerator = InstructionsGenerator
generate_claude_md = generate_instructions
