"""Instructions file generation for project onboarding.

Generates project-specific instructions content (CLAUDE.md, .cursor/rules/raise.mdc,
.windsurf/rules/raise.md, etc.) from .raise/ canonical sources.  A .raise/ directory
must exist before generation — ``rai init`` always creates it first.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

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
        identity_path = raise_dir / "rai" / "identity" / "core.md"
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
            identity_text = identity_path.read_text(encoding="utf-8")
            self._add_identity_section(lines, identity_text)

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

    def _add_identity_section(self, lines: list[str], identity_text: str) -> None:
        """Extract and add Rai Identity section from core.md."""
        lines.append("## Rai Identity")
        lines.append("")

        # Extract Values
        values = self._extract_values(identity_text)
        if values:
            lines.append("### Values")
            for i, (name, summary) in enumerate(values, 1):
                lines.append(f"{i}. {name} \u2014 {summary}")
            lines.append("")

        # Extract Boundaries
        i_will, i_wont = self._extract_boundaries(identity_text)
        if i_will or i_wont:
            lines.append("### Boundaries")
            if i_will:
                lines.append("I Will: " + ", ".join(i_will))
            if i_wont:
                lines.append("I Won't: " + ", ".join(i_wont))
            lines.append("")

        # Extract Principles (from the Internalized Philosophy table if present)
        principles = self._extract_principles_from_identity(identity_text)
        if principles:
            lines.append("### Principles")
            for i, (name, summary) in enumerate(principles, 1):
                lines.append(f"{i}. {name} \u2014 {summary}")
            lines.append("")

    def _extract_values(self, text: str) -> list[tuple[str, str]]:
        """Extract value name + summary pairs from identity core.md.

        Looks for ### N. Name headings followed by bullet points.
        Condenses all bullets into a comma-separated summary.
        """
        values: list[tuple[str, str]] = []
        # Match ### N. Name followed by bullet list (within Values section)
        pattern = r"###\s+\d+\.\s+(.+)\n((?:- .+\n)*)"
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            bullets = match.group(2).strip()
            # Condense ALL bullets into a comma-separated short summary
            bullet_texts = [
                b.lstrip("- ").strip() for b in bullets.split("\n") if b.strip()
            ]
            if bullet_texts:
                # Strip leading pronouns and clean up each bullet
                cleaned: list[str] = []
                for bt in bullet_texts:
                    # Remove "I'll " / "I'm " prefix for conciseness
                    bt = re.sub(r"^I'll\s+", "", bt)
                    bt = re.sub(r"^I'm not .+ — I'm ", "", bt)
                    bt = bt.rstrip(".")
                    # Remove surrounding quotes (only if both present)
                    if bt.startswith('"') and bt.endswith('"'):
                        bt = bt[1:-1]
                    # Lower-case the first char for inline style
                    if bt and bt[0].isupper():
                        bt = bt[0].lower() + bt[1:]
                    cleaned.append(bt)
                summary = ", ".join(cleaned)
            else:
                summary = name
            values.append((name, summary))
        return values

    def _extract_boundaries(self, text: str) -> tuple[list[str], list[str]]:
        """Extract I Will / I Won't lists from identity core.md."""
        i_will: list[str] = []
        i_wont: list[str] = []

        # Find "### I Will" section
        will_match = re.search(r"###\s+I Will\s*\n((?:- .+\n)*)", text, re.IGNORECASE)
        if will_match:
            for line in will_match.group(1).strip().split("\n"):
                item = line.lstrip("- ").strip()
                if item:
                    # Lower-case and remove trailing periods for compact format
                    item = item[0].lower() + item[1:] if item else item
                    item = item.rstrip(".")
                    i_will.append(item)

        # Find "### I Won't" section
        wont_match = re.search(r"###\s+I Won't\s*\n((?:- .+\n)*)", text, re.IGNORECASE)
        if wont_match:
            for line in wont_match.group(1).strip().split("\n"):
                item = line.lstrip("- ").strip()
                if item:
                    item = item[0].lower() + item[1:] if item else item
                    item = item.rstrip(".")
                    i_wont.append(item)

        return i_will, i_wont

    def _extract_principles_from_identity(self, text: str) -> list[tuple[str, str]]:
        """Extract principles from the Internalized Philosophy table."""
        principles: list[tuple[str, str]] = []
        # Find the "Internalized Philosophy" section first to avoid
        # matching other tables (e.g. comparison tables) in the file
        philosophy_match = re.search(
            r"##\s+Internalized Philosophy\s*\n(.*?)(?=\n---|\n##|\Z)",
            text,
            re.DOTALL,
        )
        if not philosophy_match:
            return principles

        section_text = philosophy_match.group(1)

        # Look for table rows with | **Name** | description |
        pattern = r"\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|"
        for match in re.finditer(pattern, section_text):
            name = match.group(1).strip()
            desc = match.group(2).strip()
            # Skip table header separators
            if name.startswith("-"):
                continue
            # Clean up description
            desc = desc.rstrip(".")
            if desc.startswith("I "):
                # Condense: "I push back on over-engineering..." -> short form
                desc = desc[0].lower() + desc[1:]
            principles.append((name, desc))
        return principles

    def _add_process_rules_section(
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
            "| notes: types: decision, insight, task_done, note (default: note)"
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
            '- wrong: rai backlog create RAISE --summary "Title" '
            '| right: rai backlog create "Title" -p RAISE '
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
    agent_config: AgentConfig | None = None,
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
