"""Instructions file generation for project onboarding.

Generates project-specific instructions content (CLAUDE.md, .cursor/rules/raise.mdc,
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
    to produce a comprehensive instructions file (e.g. CLAUDE.md).
    """

    def generate(
        self,
        project_name: str,
        detection: DetectionResult,
        conventions: ConventionResult | None = None,
        *,
        project_path: Path,
    ) -> str:
        """Generate CLAUDE.md content from .raise/ canonical sources.

        Args:
            project_name: Name of the project.
            detection: Project detection result (type, file count).
            conventions: Optional convention detection result (unused, kept
                for backward compatibility).
            project_path: Project root path containing .raise/ directory.

        Returns:
            Markdown content for CLAUDE.md.
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
        """Generate CLAUDE.md for a RaiSE project from .raise/ sources.

        Reads identity, methodology, manifest, and optional integration
        configs to produce a comprehensive CLAUDE.md.
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

        # Load sources
        identity_path = raise_dir / "rai" / "identity" / "core.yaml"
        methodology_path = raise_dir / "rai" / "framework" / "methodology.yaml"
        manifest_path = raise_dir / "manifest.yaml"
        jira_path = raise_dir / "jira.yaml"

        methodology: dict[str, Any] = {}
        if methodology_path.is_file():
            methodology = yaml.safe_load(methodology_path.read_text(encoding="utf-8"))

        manifest: dict[str, Any] = {}
        if manifest_path.is_file():
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

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

        # External Integrations (only if jira.yaml exists)
        if jira_path.is_file():
            self._add_integrations_section(lines)

        # File Operations (static)
        self._add_file_operations_section(lines)

        # Post-Compaction (static)
        self._add_post_compaction_section(lines)

        return "\n".join(lines)

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
        """Add CLI Quick Reference section (static content)."""
        lines.append("## CLI Quick Reference")
        lines.append("")
        lines.append("### Core")
        lines.append(
            "- cmd: rai init | sig: [--name TEXT] [--path PATH] [--detect] "
            "| notes: --detect analyzes conventions"
        )
        lines.append("")
        lines.append("### Session")
        lines.append(
            "- cmd: rai session start | sig: [--name TEXT] [--project TEXT] "
            "[--agent TEXT] [--context] | notes: --name first-time only, --context for bundle"
        )
        lines.append(
            "- cmd: rai session close | sig: [--summary TEXT] [--type TEXT] "
            "[--pattern TEXT] [--state-file TEXT] [--session TEXT] "
            "| notes: --state-file for structured close, --pattern repeatable"
        )
        lines.append(
            "- cmd: rai session context | sig: --sections/-s TEXT --project/-p TEXT "
            "| notes: sections: governance,behavioral,coaching,deadlines,progress"
        )
        lines.append(
            "- cmd: rai session journal add | sig: TEXT [--type TYPE] "
            "| notes: add decision/insight/task to session"
        )
        lines.append(
            "- cmd: rai session journal show | sig: [--compact] [--project TEXT] "
            "| notes: --compact for post-compaction restore"
        )
        lines.append("")
        lines.append("### Graph")
        lines.append(
            "- cmd: rai graph build | sig: [--output PATH] [--no-diff] "
            "| notes: NO --project flag, runs from CWD"
        )
        lines.append(
            "- cmd: rai graph query | sig: QUERY_STR [--types TYPE] "
            "[--strategy keyword_search|concept_lookup] [--limit N] "
            "[--format human|json|compact] | notes: QUERY_STR positional"
        )
        lines.append(
            "- cmd: rai graph context | sig: MODULE_ID [--format human|json] "
            "| notes: MODULE_ID positional (e.g. mod-memory)"
        )
        lines.append("")
        lines.append("### Pattern")
        lines.append(
            "- cmd: rai pattern add | sig: CONTENT [--context KEYWORDS] "
            "[--type TYPE] [--from STORY_ID] [--scope SCOPE] "
            "| notes: CONTENT positional, --from NOT --source"
        )
        lines.append("")
        lines.append("### Signal")
        lines.append(
            "- cmd: rai signal emit-work | sig: WORK_TYPE WORK_ID "
            "[--event EVENT] [--phase PHASE] "
            "| notes: WORK_TYPE=epic|story, EVENT=start|complete|blocked"
        )
        lines.append("")
        lines.append("### Discovery")
        lines.append(
            "- cmd: rai discover scan | sig: [PATH] [--language LANG] "
            "[--output human|json|summary] [--exclude PATTERN] "
            "| notes: PATH positional, --exclude repeatable"
        )
        lines.append("")
        lines.append("### Skill")
        lines.append(
            "- cmd: rai skill list|validate|check-name|scaffold "
            "| sig: [SKILL_NAME] | notes: validate checks skill structure"
        )
        lines.append(
            "- cmd: rai skill set create|list|diff "
            "| sig: [SET_NAME] | notes: manage skill sets"
        )
        lines.append("")
        lines.append("### Backlog (requires -a jira when multiple adapters)")
        lines.append(
            "- cmd: rai backlog create | sig: SUMMARY -p PROJECT [-t TYPE] "
            "[-d DESC] [-l LABELS] [--parent KEY] "
            "| notes: SUMMARY positional, -p required"
        )
        lines.append(
            "- cmd: rai backlog search | sig: QUERY [-n LIMIT] [-a ADAPTER] "
            "[-f FORMAT] | notes: QUERY positional, JQL for Jira"
        )
        lines.append(
            "- cmd: rai backlog get | sig: KEY [-a ADAPTER] "
            "| notes: single issue details"
        )
        lines.append(
            "- cmd: rai backlog get-comments | sig: KEY [-a ADAPTER] "
            "| notes: issue comments"
        )
        lines.append(
            "- cmd: rai backlog transition | sig: KEY STATUS [-a ADAPTER] "
            "| notes: both positional"
        )
        lines.append(
            "- cmd: rai backlog batch-transition | sig: KEYS STATUS [-a ADAPTER] "
            "| notes: KEYS comma-separated"
        )
        lines.append(
            "- cmd: rai backlog comment | sig: KEY BODY [-a ADAPTER] "
            "| notes: both positional"
        )
        lines.append(
            "- cmd: rai backlog link | sig: SOURCE TARGET LINK_TYPE [-a ADAPTER] "
            "| notes: all 3 positional"
        )
        lines.append(
            "- cmd: rai backlog update | sig: KEY [-s SUMMARY] [-l LABELS] "
            "[--priority TEXT] [--assignee TEXT] "
            "| notes: KEY positional, named flags for fields"
        )
        lines.append("")
        lines.append("### Docs (documentation targets \u2014 Confluence etc.)")
        lines.append(
            "- cmd: rai docs publish | sig: ARTIFACT_TYPE [--title TEXT] "
            "[-t TARGET] | notes: ARTIFACT_TYPE positional (roadmap, adr, etc.)"
        )
        lines.append(
            "- cmd: rai docs get | sig: IDENTIFIER [-t TARGET] "
            "| notes: page ID on remote target"
        )
        lines.append(
            "- cmd: rai docs search | sig: QUERY [-n LIMIT] [-t TARGET] "
            "| notes: QUERY positional"
        )
        lines.append("")
        lines.append("### MCP")
        lines.append("- cmd: rai mcp list | notes: registered servers in .raise/mcp/")
        lines.append("- cmd: rai mcp health | sig: SERVER | notes: SERVER positional")
        lines.append("- cmd: rai mcp tools | sig: SERVER | notes: list tools on server")
        lines.append(
            "- cmd: rai mcp call | sig: SERVER TOOL [--args JSON] [--verbose] "
            "| notes: both positional"
        )
        lines.append(
            "- cmd: rai mcp install | sig: PACKAGE --type uvx|npx|pip --name TEXT "
            "[--env TEXT] [--module TEXT] | notes: PACKAGE positional"
        )
        lines.append(
            "- cmd: rai mcp scaffold | sig: NAME --command TEXT [--args TEXT] "
            "[--env TEXT] | notes: NAME positional"
        )
        lines.append("")
        lines.append("### Gate")
        lines.append(
            "- cmd: rai gate list | sig: [-f FORMAT] | notes: discovered workflow gates"
        )
        lines.append(
            "- cmd: rai gate check | sig: [GATE_ID] [--all/-a] [-f FORMAT] "
            "| notes: exit 0 all pass, 1 any fail"
        )
        lines.append("")
        lines.append("### Adapter")
        lines.append(
            "- cmd: rai adapter list | sig: [-f FORMAT] "
            "| notes: registered adapters by entry point"
        )
        lines.append(
            "- cmd: rai adapter check | sig: [-f FORMAT] "
            "| notes: validate against Protocol contracts"
        )
        lines.append(
            "- cmd: rai adapter validate | sig: FILE "
            "| notes: validate declarative YAML adapter config"
        )
        lines.append("")
        lines.append("### Release")
        lines.append(
            "- cmd: rai release check | sig: [-p PATH] | notes: run 10 quality gates"
        )
        lines.append(
            "- cmd: rai release publish | sig: --bump/-b "
            "major|minor|patch|alpha|beta|rc|release "
            "[--version/-v TEXT] [--dry-run] [--skip-check] "
            "| notes: --bump or --version required"
        )
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
            "| why: named flags (-s, -l, --priority, --assignee)"
        )
        lines.append("")

    def _add_integrations_section(self, lines: list[str]) -> None:
        """Add External Integrations section."""
        lines.append("## External Integrations")
        lines.append(
            "- Jira config: `.raise/jira.yaml` \u2014 team identifiers, workflows, "
            "transition IDs. Read just-in-time via `rai backlog` CLI."
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
        >>> Path("CLAUDE.md").write_text(content)
    """
    generator = InstructionsGenerator()
    return generator.generate(
        project_name, detection, conventions, project_path=project_path
    )


# Backward-compat alias
ClaudeMdGenerator = InstructionsGenerator
generate_claude_md = generate_instructions
