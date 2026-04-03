"""Tests for GraphBuilder."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from raise_cli.config.agents import get_agent_config
from raise_cli.context.builder import GraphBuilder
from raise_core.graph.models import GraphNode


class TestGraphBuilderInit:
    """Tests for GraphBuilder initialization."""

    def test_initializes_with_project_root(self, tmp_path: Path) -> None:
        """Should accept project root path."""
        builder = GraphBuilder(project_root=tmp_path)
        assert builder.project_root == tmp_path

    def test_uses_cwd_when_no_root_provided(self) -> None:
        """Should use current directory when no root provided."""
        builder = GraphBuilder()
        assert builder.project_root == Path.cwd()

    def test_initializes_with_ide_config(self, tmp_path: Path) -> None:
        """Should accept and store IDE configuration."""
        config = get_agent_config("antigravity")
        builder = GraphBuilder(project_root=tmp_path, agent_config=config)
        assert builder.ide_config.agent_type == "antigravity"
        assert builder.ide_config.skills_dir == ".agent/skills"

    def test_defaults_to_claude_ide_config(self, tmp_path: Path) -> None:
        """Should default to Claude IDE config when none provided."""
        builder = GraphBuilder(project_root=tmp_path)
        assert builder.ide_config.agent_type == "claude"
        assert builder.ide_config.skills_dir == ".claude/skills"


class TestLoadGovernance:
    """Tests for load_governance method."""

    def test_returns_graph_nodes_from_extractor(self, tmp_path: Path) -> None:
        """Extractor returns GraphNode directly — no conversion needed."""
        mock_node = GraphNode(
            id="principle-1",
            type="principle",
            content="This is a core principle.",
            source_file="framework/reference/constitution.md",
            created="2026-01-01T00:00:00+00:00",
            metadata={"principle_number": "§1"},
        )

        builder = GraphBuilder(project_root=tmp_path)

        with patch.object(builder, "_get_governance_extractor") as mock_extractor:
            mock_extractor.return_value.extract_all.return_value = [mock_node]
            nodes = builder.load_governance()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "principle-1"
        assert node.type == "principle"
        assert node.content == "This is a core principle."
        assert node.source_file == "framework/reference/constitution.md"

    def test_handles_empty_extraction(self, tmp_path: Path) -> None:
        """Should return empty list when no concepts extracted."""
        builder = GraphBuilder(project_root=tmp_path)

        with patch.object(builder, "_get_governance_extractor") as mock_extractor:
            mock_extractor.return_value.extract_all.return_value = []
            nodes = builder.load_governance()

        assert nodes == []


class TestLoadMemory:
    """Tests for load_memory method."""

    def test_loads_patterns_from_jsonl(self, tmp_path: Path) -> None:
        """Should load patterns from patterns.jsonl."""
        # Create .raise/rai/memory structure
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        patterns_file = memory_dir / "patterns.jsonl"
        patterns_file.write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "codebase",
                    "content": "Singleton pattern for testing",
                    "context": ["testing", "patterns"],
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "PAT-001"
        assert node.type == "pattern"
        assert node.content == "Singleton pattern for testing"
        assert "testing" in node.metadata.get("context", [])

    def test_loads_calibration_from_jsonl(self, tmp_path: Path) -> None:
        """Should load calibration from calibration.jsonl."""
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        calibration_file = memory_dir / "calibration.jsonl"
        calibration_file.write_text(
            json.dumps(
                {
                    "id": "CAL-001",
                    "feature": "F1.1",
                    "name": "Project Scaffolding",
                    "size": "S",
                    "sp": 3,
                    "actual_min": 30,
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "CAL-001"
        assert node.type == "calibration"
        assert "F1.1" in node.content

    def test_loads_sessions_from_jsonl(self, tmp_path: Path) -> None:
        """Should load sessions from personal/sessions/index.jsonl."""
        # Sessions now only load from personal directory (multi-dev architecture)
        sessions_dir = tmp_path / ".raise/rai" / "personal" / "sessions"
        sessions_dir.mkdir(parents=True)

        sessions_file = sessions_dir / "index.jsonl"
        sessions_file.write_text(
            json.dumps(
                {
                    "id": "SES-001",
                    "date": "2026-02-01",
                    "type": "story",
                    "topic": "E3 Implementation",
                    "outcomes": ["Feature complete", "Tests passing"],
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "SES-001"
        assert node.type == "session"
        assert "E3 Implementation" in node.content

    def test_handles_missing_memory_directory(self, tmp_path: Path) -> None:
        """Should return empty list if .raise/rai/memory doesn't exist."""
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert nodes == []

    def test_loads_all_memory_types(self, tmp_path: Path) -> None:
        """Should load patterns, calibration, and sessions together."""
        # Project directory for patterns and calibration
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        # Personal directory for sessions (multi-dev architecture)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        sessions_dir = personal_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "process",
                    "content": "Pattern",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )
        (memory_dir / "calibration.jsonl").write_text(
            json.dumps(
                {
                    "id": "CAL-001",
                    "feature": "F1.1",
                    "name": "Test",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )
        (sessions_dir / "index.jsonl").write_text(
            json.dumps({"id": "SES-001", "date": "2026-02-01", "topic": "Session"})
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 3
        types = {n.type for n in nodes}
        assert types == {"pattern", "calibration", "session"}


class TestLoadMemoryBaseVersion:
    """Tests for base/version passthrough in graph builder (F14.6)."""

    def test_base_pattern_preserves_base_version_in_metadata(
        self, tmp_path: Path
    ) -> None:
        """Base pattern fields should pass through to GraphNode metadata."""
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "BASE-001",
                    "type": "process",
                    "content": "TDD cycle discipline",
                    "context": ["tdd", "testing"],
                    "base": True,
                    "version": 1,
                    "created": "2026-02-05",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.metadata.get("base") is True
        assert node.metadata.get("version") == 1

    def test_personal_pattern_has_no_base_version(self, tmp_path: Path) -> None:
        """Personal patterns should not have base/version in metadata."""
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "codebase",
                    "content": "My custom pattern",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert "base" not in node.metadata
        assert "version" not in node.metadata


class TestLoadMemoryMultiSource:
    """Tests for multi-source memory loading (global, project, personal)."""

    def test_loads_from_global_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should load patterns from ~/.rai/ with global scope."""
        # Setup global directory
        global_rai = tmp_path / "global_rai"
        global_rai.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_rai))

        (global_rai / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-GLOBAL",
                    "type": "universal",
                    "content": "Universal pattern",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "PAT-GLOBAL"
        assert node.metadata.get("scope") == "global"

    def test_loads_from_project_directory(self, tmp_path: Path) -> None:
        """Should load patterns from .raise/rai/memory/ with project scope."""
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-PROJECT",
                    "type": "codebase",
                    "content": "Project pattern",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "PAT-PROJECT"
        assert node.metadata.get("scope") == "project"

    def test_loads_from_personal_directory(self, tmp_path: Path) -> None:
        """Should load patterns from .raise/rai/personal/ with personal scope."""
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)

        (personal_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-PERSONAL",
                    "type": "process",
                    "content": "Personal pattern",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "PAT-PERSONAL"
        assert node.metadata.get("scope") == "personal"

    def test_loads_from_all_three_tiers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should load from global, project, and personal directories."""
        # Setup global
        global_rai = tmp_path / "global_rai"
        global_rai.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_rai))
        (global_rai / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-G1",
                    "type": "universal",
                    "content": "Global",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        # Setup project
        project_memory = tmp_path / ".raise/rai" / "memory"
        project_memory.mkdir(parents=True)
        (project_memory / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-P1",
                    "type": "codebase",
                    "content": "Project",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        # Setup personal
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-L1",
                    "type": "process",
                    "content": "Personal",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 3
        scopes = {n.metadata.get("scope") for n in nodes}
        assert scopes == {"global", "project", "personal"}

    def test_loads_calibration_from_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should load calibration from ~/.rai/ with global scope."""
        global_rai = tmp_path / "global_rai"
        global_rai.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_rai))

        (global_rai / "calibration.jsonl").write_text(
            json.dumps(
                {
                    "id": "CAL-GLOBAL",
                    "feature": "F1.1",
                    "name": "Global Cal",
                    "size": "S",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        assert nodes[0].id == "CAL-GLOBAL"
        assert nodes[0].metadata.get("scope") == "global"

    def test_loads_sessions_from_personal_only(self, tmp_path: Path) -> None:
        """Sessions should only load from personal directory (developer-specific)."""
        # Project sessions (should NOT be loaded in multi-dev mode)
        project_sessions = tmp_path / ".raise/rai" / "memory" / "sessions"
        project_sessions.mkdir(parents=True)
        (project_sessions / "index.jsonl").write_text(
            json.dumps(
                {
                    "id": "SES-PROJECT",
                    "date": "2026-02-01",
                    "type": "story",
                    "topic": "Project session",
                }
            )
            + "\n"
        )

        # Personal sessions (SHOULD be loaded)
        personal_sessions = tmp_path / ".raise/rai" / "personal" / "sessions"
        personal_sessions.mkdir(parents=True)
        (personal_sessions / "index.jsonl").write_text(
            json.dumps(
                {
                    "id": "SES-PERSONAL",
                    "date": "2026-02-01",
                    "type": "story",
                    "topic": "Personal session",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # Should only have personal session
        session_nodes = [n for n in nodes if n.type == "session"]
        assert len(session_nodes) == 1
        assert session_nodes[0].id == "SES-PERSONAL"
        assert session_nodes[0].metadata.get("scope") == "personal"


class TestPrecedenceLogic:
    """Tests for memory scope precedence (personal > project > global)."""

    def test_personal_overrides_project(self, tmp_path: Path) -> None:
        """Personal scope should override project scope for same ID."""
        # Project pattern
        project_dir = tmp_path / ".raise/rai" / "memory"
        project_dir.mkdir(parents=True)
        (project_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "codebase",
                    "content": "Project version",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        # Personal pattern with same ID
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "codebase",
                    "content": "Personal override",
                    "created": "2026-02-01",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # Should only have one PAT-001, from personal
        pat_nodes = [n for n in nodes if n.id == "PAT-001"]
        assert len(pat_nodes) == 1
        assert pat_nodes[0].content == "Personal override"
        assert pat_nodes[0].metadata.get("scope") == "personal"

    def test_project_overrides_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Project scope should override global scope for same ID."""
        # Global pattern
        global_dir = tmp_path / "global_rai"
        global_dir.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_dir))
        (global_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-002",
                    "type": "universal",
                    "content": "Global version",
                    "created": "2026-01-30",
                }
            )
            + "\n"
        )

        # Project pattern with same ID
        project_dir = tmp_path / ".raise/rai" / "memory"
        project_dir.mkdir(parents=True)
        (project_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-002",
                    "type": "codebase",
                    "content": "Project override",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # Should only have one PAT-002, from project
        pat_nodes = [n for n in nodes if n.id == "PAT-002"]
        assert len(pat_nodes) == 1
        assert pat_nodes[0].content == "Project override"
        assert pat_nodes[0].metadata.get("scope") == "project"

    def test_personal_overrides_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Personal scope should override global scope for same ID."""
        # Global pattern
        global_dir = tmp_path / "global_rai"
        global_dir.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_dir))
        (global_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-003",
                    "type": "universal",
                    "content": "Global version",
                    "created": "2026-01-30",
                }
            )
            + "\n"
        )

        # Personal pattern with same ID (skipping project)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-003",
                    "type": "process",
                    "content": "Personal override",
                    "created": "2026-02-01",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # Should only have one PAT-003, from personal
        pat_nodes = [n for n in nodes if n.id == "PAT-003"]
        assert len(pat_nodes) == 1
        assert pat_nodes[0].content == "Personal override"
        assert pat_nodes[0].metadata.get("scope") == "personal"

    def test_unique_ids_all_preserved(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unique IDs from all tiers should be preserved."""
        # Global pattern
        global_dir = tmp_path / "global_rai"
        global_dir.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_dir))
        (global_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-G1",
                    "type": "universal",
                    "content": "Global",
                    "created": "2026-01-30",
                }
            )
            + "\n"
        )

        # Project pattern (different ID)
        project_dir = tmp_path / ".raise/rai" / "memory"
        project_dir.mkdir(parents=True)
        (project_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-P1",
                    "type": "codebase",
                    "content": "Project",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        # Personal pattern (different ID)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-L1",
                    "type": "process",
                    "content": "Personal",
                    "created": "2026-02-01",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # All three should be preserved
        assert len(nodes) == 3
        ids = {n.id for n in nodes}
        assert ids == {"PAT-G1", "PAT-P1", "PAT-L1"}


class TestLoadSkills:
    """Tests for load_skills method."""

    def test_loads_skills_from_directory(self, tmp_path: Path) -> None:
        """Should load skills from .claude/skills directory."""
        skills_dir = tmp_path / ".claude" / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)

        (skills_dir / "SKILL.md").write_text(
            dedent("""\
            ---
            name: test-skill
            description: A test skill
            ---
            # Test
        """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_skills()

        assert len(nodes) == 1
        assert nodes[0].id == "/test-skill"
        assert nodes[0].type == "skill"

    def test_handles_missing_skills_directory(self, tmp_path: Path) -> None:
        """Should return empty list if .claude/skills doesn't exist."""
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_skills()

        assert nodes == []

    def test_load_skills_with_antigravity_config(self, tmp_path: Path) -> None:
        """Should load skills from .agent/skills with antigravity config."""
        skills_dir = tmp_path / ".agent" / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)

        (skills_dir / "SKILL.md").write_text(
            dedent("""\
            ---
            name: test-skill
            description: A test skill
            ---
            # Test
        """)
        )

        config = get_agent_config("antigravity")
        builder = GraphBuilder(project_root=tmp_path, agent_config=config)
        nodes = builder.load_skills()

        assert len(nodes) == 1
        assert nodes[0].id == "/test-skill"


class TestLoadComponents:
    """Tests for load_components method."""

    def test_loads_components_from_validated_json(self, tmp_path: Path) -> None:
        """Should load components from components-validated.json."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "source_file": "work/discovery/components-draft.yaml",
                    "component_count": 2,
                    "components": [
                        {
                            "id": "comp-scanner-symbol",
                            "type": "component",
                            "content": "Core data model for code symbols",
                            "source_file": "src/discovery/scanner.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "Symbol",
                                "kind": "class",
                                "line": 44,
                                "category": "model",
                            },
                        },
                        {
                            "id": "comp-scanner-scan-dir",
                            "type": "component",
                            "content": "Scan directory for symbols",
                            "source_file": "src/discovery/scanner.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "scan_directory",
                                "kind": "function",
                                "line": 100,
                                "category": "utility",
                            },
                        },
                    ],
                }
            )
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert len(nodes) == 2
        assert nodes[0].id == "comp-scanner-symbol"
        assert nodes[0].type == "component"
        assert nodes[0].content == "Core data model for code symbols"
        assert nodes[0].metadata.get("name") == "Symbol"
        assert nodes[0].metadata.get("category") == "model"

    def test_handles_missing_components_file(self, tmp_path: Path) -> None:
        """Should return empty list if components-validated.json doesn't exist."""
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []

    def test_handles_empty_components_list(self, tmp_path: Path) -> None:
        """Should return empty list if components array is empty."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [],
                }
            )
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []

    def test_handles_invalid_json(self, tmp_path: Path) -> None:
        """Should return empty list on invalid JSON."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text("not valid json")

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []


class TestLoadArchitecture:
    """Tests for load_architecture method."""

    def test_loads_module_from_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Should parse YAML frontmatter from architecture module docs."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "discovery.yaml").write_text(
            dedent("""\
            type: module
            name: discovery
            purpose: "Codebase analysis and scanning"
            status: current
            depends_on: [core, schemas]
            depended_by: [cli, context]
            components: 42
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "mod-discovery"
        assert node.type == "module"
        assert node.content == "Codebase analysis and scanning"
        assert node.source_file == "governance/architecture/modules/discovery.yaml"
        assert node.metadata["depends_on"] == ["core", "schemas"]
        assert node.metadata["depended_by"] == ["cli", "context"]
        assert node.metadata["components"] == 42

    def test_loads_multiple_modules(self, tmp_path: Path) -> None:
        """Should load all module docs from architecture/modules/."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        for name in ["core", "schemas", "discovery"]:
            (modules_dir / f"{name}.yaml").write_text(
                dedent(f"""\
                type: module
                name: {name}
                purpose: "{name} module"
                status: current
                depends_on: []
                """)
            )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert len(nodes) == 3
        ids = {n.id for n in nodes}
        assert ids == {"mod-core", "mod-schemas", "mod-discovery"}

    def test_handles_missing_architecture_directory(self, tmp_path: Path) -> None:
        """Should return empty list if governance/architecture/ doesn't exist."""
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert nodes == []

    def test_skips_files_without_module_type(self, tmp_path: Path) -> None:
        """Should skip files where frontmatter type is not 'module'."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "index.yaml").write_text(
            dedent("""\
            type: architecture_index
            project: raise-cli
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert nodes == []

    def test_skips_files_with_invalid_yaml(self, tmp_path: Path) -> None:
        """Should skip files with unparseable YAML frontmatter."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "broken.yaml").write_text("not: [invalid")

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert nodes == []

    def test_creates_depends_on_edges(self, tmp_path: Path) -> None:
        """Should create depends_on edges between module nodes."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "discovery.yaml").write_text(
            dedent("""\
            type: module
            name: discovery
            purpose: "Code scanning"
            depends_on: [core, schemas]
            """)
        )
        (modules_dir / "core.yaml").write_text(
            dedent("""\
            type: module
            name: core
            purpose: "Shared utilities"
            depends_on: []
            """)
        )
        (modules_dir / "schemas.yaml").write_text(
            dedent("""\
            type: module
            name: schemas
            purpose: "Pydantic models"
            depends_on: []
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()
        edges = builder.infer_relationships(nodes)

        depends_on_edges = [e for e in edges if e.type == "depends_on"]
        assert len(depends_on_edges) == 2

        # discovery → core and discovery → schemas
        targets = {e.target for e in depends_on_edges if e.source == "mod-discovery"}
        assert targets == {"mod-core", "mod-schemas"}

    def test_build_includes_architecture_modules(self, tmp_path: Path) -> None:
        """Build should include architecture module nodes in graph."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "core.yaml").write_text(
            dedent("""\
            type: module
            name: core
            purpose: "Shared utilities"
            depends_on: []
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        assert graph.node_count == 1
        node = graph.get_concept("mod-core")
        assert node is not None
        assert node.type == "module"


class TestLoadArchitectureDocTypes:
    """Tests for architecture doc type ingestion (S15.1)."""

    def test_loads_architecture_context_doc(self, tmp_path: Path) -> None:
        """Should parse architecture_context doc into architecture node."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "system-context.yaml").write_text(
            dedent("""\
            type: architecture_context
            project: raise-cli
            version: 2.0.0-alpha
            status: current
            tech_stack:
              language: "Python 3.12+"
              framework: "Pydantic AI"
              cli: "Typer"
            external_dependencies:
              - "Git (version control)"
              - "ripgrep (fast content search)"
            users:
              - "RaiSE Engineers"
              - "Rai (AI partner)"
            governed_by:
              - "framework/reference/constitution.md"
              - "governance/guardrails.md"
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.type == "architecture"]
        assert len(arch_nodes) == 1
        node = arch_nodes[0]
        assert node.id == "arch-context"
        assert node.type == "architecture"
        assert "Python 3.12+" in node.content
        assert node.source_file == "governance/architecture/system-context.yaml"
        assert node.metadata["arch_type"] == "architecture_context"
        assert node.metadata["tech_stack"]["language"] == "Python 3.12+"
        assert len(node.metadata["external_dependencies"]) == 2
        assert len(node.metadata["governed_by"]) == 2

    def test_loads_architecture_design_doc_with_string_layers(
        self, tmp_path: Path
    ) -> None:
        """Should not crash when layers are strings instead of dicts (RS-6)."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "system-design.md").write_text(
            dedent("""\
            ---
            type: architecture_design
            project: test-project
            status: current
            layers:
              - Frontend
              - Backend
              - Database
            ---

            # System Design
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.type == "architecture"]
        assert len(arch_nodes) == 1
        assert arch_nodes[0].id == "arch-design"

    def test_loads_architecture_design_doc(self, tmp_path: Path) -> None:
        """Should parse architecture_design doc into architecture node."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "system-design.yaml").write_text(
            dedent("""\
            type: architecture_design
            project: raise-cli
            status: current
            layers:
              - name: leaf
                modules: [core, config, schemas]
                description: "Zero internal dependencies"
              - name: domain
                modules: [governance, discovery, skills, telemetry]
                description: "Independent domain logic"
              - name: integration
                modules: [context, memory, onboarding, output]
                description: "Combines domains"
              - name: orchestration
                modules: [cli]
                description: "User-facing entry points"
            architectural_decisions:
              - "ADR-012: Skills + Toolkit"
              - "ADR-019: Unified graph"
            guardrails_reference: "governance/guardrails.md"
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.type == "architecture"]
        assert len(arch_nodes) == 1
        node = arch_nodes[0]
        assert node.id == "arch-design"
        assert node.type == "architecture"
        assert "leaf" in node.content
        assert "orchestration" in node.content
        assert node.metadata["arch_type"] == "architecture_design"
        assert len(node.metadata["layers"]) == 4
        assert node.metadata["layers"][0]["name"] == "leaf"
        assert node.metadata["layers"][0]["modules"] == ["core", "config", "schemas"]

    def test_loads_architecture_domain_model_doc(self, tmp_path: Path) -> None:
        """Should parse architecture_domain_model doc into architecture node."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "domain-model.yaml").write_text(
            dedent("""\
            type: architecture_domain_model
            project: raise-cli
            status: current
            bounded_contexts:
              - name: governance
                modules: [governance]
                description: "Extract structured knowledge"
              - name: ontology
                modules: [context, memory]
                description: "Persist and query knowledge"
              - name: discovery
                modules: [discovery]
                description: "Scan codebases"
            shared_kernel:
              modules: [config, core, schemas]
              description: "Foundation utilities"
            application_layer:
              modules: [cli]
              description: "Thin orchestration shell"
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.type == "architecture"]
        assert len(arch_nodes) == 1
        node = arch_nodes[0]
        assert node.id == "arch-domain-model"
        assert node.type == "architecture"
        assert "governance" in node.content
        assert "ontology" in node.content
        assert node.metadata["arch_type"] == "architecture_domain_model"
        assert len(node.metadata["bounded_contexts"]) == 3
        assert node.metadata["shared_kernel"]["modules"] == [
            "config",
            "core",
            "schemas",
        ]

    def test_skips_architecture_index_doc(self, tmp_path: Path) -> None:
        """Should skip architecture_index docs (generated summary)."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "index.yaml").write_text(
            dedent("""\
            type: architecture_index
            project: raise-cli
            generated: "2026-02-08"
            modules: 13
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert nodes == []

    def test_scans_parent_and_modules_directories(self, tmp_path: Path) -> None:
        """Should load from both governance/architecture/ and modules/."""
        arch_dir = tmp_path / "governance" / "architecture"
        modules_dir = arch_dir / "modules"
        modules_dir.mkdir(parents=True)

        # Parent-level architecture doc
        (arch_dir / "system-context.yaml").write_text(
            dedent("""\
            type: architecture_context
            project: raise-cli
            status: current
            tech_stack:
              language: "Python 3.12+"
            external_dependencies: []
            users: []
            governed_by: []
            """)
        )

        # Module-level doc
        (modules_dir / "core.yaml").write_text(
            dedent("""\
            type: module
            name: core
            purpose: "Shared utilities"
            depends_on: []
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert len(nodes) == 2
        types = {n.type for n in nodes}
        assert types == {"architecture", "module"}
        ids = {n.id for n in nodes}
        assert ids == {"arch-context", "mod-core"}

    def test_existing_module_parsing_unchanged(self, tmp_path: Path) -> None:
        """Module doc parsing should remain backward compatible."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "memory.yaml").write_text(
            dedent("""\
            type: module
            name: memory
            purpose: "Pattern and calibration JSONL management"
            status: current
            depends_on: [config, context]
            depended_by: [cli]
            components: 30
            constraints:
              - "JSONL is append-only"
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "mod-memory"
        assert node.type == "module"
        assert node.content == "Pattern and calibration JSONL management"
        assert node.metadata["depends_on"] == ["config", "context"]
        assert node.metadata["depended_by"] == ["cli"]
        assert node.metadata["components"] == 30
        assert node.metadata["constraints"] == ["JSONL is append-only"]


class TestBuild:
    """Tests for build method."""

    def test_builds_graph_with_all_sources(self, tmp_path: Path) -> None:
        """Should combine all sources into Graph."""
        # Setup minimal fixtures
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "process",
                    "content": "Test",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        skills_dir = tmp_path / ".claude" / "skills" / "test"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            dedent("""\
            ---
            name: test
            description: Test skill
            ---
            # Test
        """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        # Mock governance and components loaders
        with patch.object(builder, "load_governance") as mock_gov:
            mock_gov.return_value = []
            with patch.object(builder, "load_components") as mock_comp:
                mock_comp.return_value = []
                graph = builder.build()

        # Should have memory + skills
        assert graph.node_count >= 2

    def test_build_returns_unified_graph(self, tmp_path: Path) -> None:
        """Should return Graph instance."""
        from raise_core.graph.engine import Graph

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        assert isinstance(graph, Graph)

    def test_build_includes_components(self, tmp_path: Path) -> None:
        """Should include components in the built graph."""
        # Setup components file
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-test",
                            "type": "component",
                            "content": "Test component",
                            "source_file": "src/test.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {"name": "TestClass", "kind": "class"},
                        },
                    ],
                }
            )
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
        ):
            graph = builder.build()

        assert graph.node_count == 1
        node = graph.get_concept("comp-test")
        assert node is not None
        assert node.type == "component"
        assert node.content == "Test component"

    def test_build_raises_on_duplicate_node_ids(self, tmp_path: Path) -> None:
        """Should raise ValueError when duplicate node IDs are detected (RAISE-510)."""
        builder = GraphBuilder(project_root=tmp_path)

        duplicate_nodes = [
            GraphNode(
                id="comp-test-Foo",
                type="component",
                content="First Foo",
                created="2026-02-09",
            ),
            GraphNode(
                id="comp-test-Foo",
                type="component",
                content="Second Foo (collision)",
                created="2026-02-09",
            ),
        ]

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=duplicate_nodes),
            pytest.raises(ValueError, match="Duplicate node ID.*comp-test-Foo"),
        ):
            builder.build()


class TestInferRelationships:
    """Tests for infer_relationships method."""

    def test_infers_learned_from_edges(self, tmp_path: Path) -> None:
        """Should create learned_from edges from pattern.learned_from field."""
        pattern = GraphNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"learned_from": "F1.5"},
        )
        session = GraphNode(
            id="SES-010",
            type="session",
            content="F1.5 session",
            source_file=".raise/rai/memory/sessions/index.jsonl",
            created="2026-01-31",
            metadata={"topic": "F1.5 Output Module"},
        )

        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([pattern, session])

        learned_edges = [e for e in edges if e.type == "learned_from"]
        assert len(learned_edges) >= 1
        edge = learned_edges[0]
        assert edge.source == "PAT-001"
        assert edge.weight == 1.0

    def test_infers_part_of_edges(self, tmp_path: Path) -> None:
        """Should create part_of edges from feature to epic."""
        feature = GraphNode(
            id="F11.2",
            type="story",
            content="Graph Builder",
            source_file="dev/epic-e11-scope.md",
            created="2026-02-03",
            metadata={},
        )
        epic = GraphNode(
            id="E11",
            type="epic",
            content="Unified Context",
            source_file="governance/backlog.md",
            created="2026-02-03",
            metadata={},
        )

        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([feature, epic])

        part_of_edges = [e for e in edges if e.type == "part_of"]
        assert len(part_of_edges) == 1
        assert part_of_edges[0].source == "F11.2"
        assert part_of_edges[0].target == "E11"
        assert part_of_edges[0].weight == 1.0

    def test_infers_skill_prerequisite_edges(self, tmp_path: Path) -> None:
        """Should create needs_context edges from skill prerequisites."""
        skill = GraphNode(
            id="/story-plan",
            type="skill",
            content="Plan implementation tasks",
            source_file=".claude/skills/story-plan/SKILL.md",
            created="2026-02-03",
            metadata={"raise.prerequisites": "project-backlog"},
        )
        prereq = GraphNode(
            id="/project-backlog",
            type="skill",
            content="Manage project backlog",
            source_file=".claude/skills/project-backlog/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([skill, prereq])

        needs_edges = [e for e in edges if e.type == "needs_context"]
        assert len(needs_edges) == 1
        assert needs_edges[0].source == "/story-plan"
        assert needs_edges[0].target == "/project-backlog"
        assert needs_edges[0].weight == 1.0

    def test_infers_skill_next_edges(self, tmp_path: Path) -> None:
        """Should create related_to edges from skill.raise/raise.next."""
        skill = GraphNode(
            id="/rai-story-plan",
            type="skill",
            content="Plan tasks",
            source_file=".claude/skills/rai-story-plan/SKILL.md",
            created="2026-02-03",
            metadata={"raise.next": "rai-story-implement"},
        )
        next_skill = GraphNode(
            id="/rai-story-implement",
            type="skill",
            content="Implement feature",
            source_file=".claude/skills/rai-story-implement/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([skill, next_skill])

        next_edges = [
            e
            for e in edges
            if e.source == "/rai-story-plan" and e.target == "/rai-story-implement"
        ]
        assert len(next_edges) == 1
        assert next_edges[0].type == "related_to"
        assert next_edges[0].weight == 1.0

    def test_infers_related_to_by_shared_keywords(self, tmp_path: Path) -> None:
        """Should create related_to edges for concepts with shared keywords."""
        pattern = GraphNode(
            id="PAT-012",
            type="pattern",
            content="Design-first eliminates ambiguity in implementation planning",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"context": ["planning", "implementation"]},
        )
        skill = GraphNode(
            id="/story-plan",
            type="skill",
            content="Planning implementation tasks for feature development",
            source_file=".claude/skills/story-plan/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([pattern, skill])

        related_edges = [e for e in edges if e.type == "related_to"]
        # Should find shared keywords "planning" and "implementation"
        assert len(related_edges) >= 1
        # Inferred edges have weight < 1.0
        inferred = [e for e in related_edges if e.weight < 1.0]
        assert len(inferred) >= 1

    def test_returns_empty_for_no_nodes(self, tmp_path: Path) -> None:
        """Should return empty list when no nodes provided."""
        builder = GraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([])

        assert edges == []

    def test_build_includes_inferred_edges(self, tmp_path: Path) -> None:
        """Build should include edges from infer_relationships."""
        # Project directory for patterns
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)

        # Personal directory for sessions (multi-dev architecture)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        sessions_dir = personal_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        # Pattern with learned_from
        (memory_dir / "patterns.jsonl").write_text(
            json.dumps(
                {
                    "id": "PAT-001",
                    "type": "process",
                    "content": "Test pattern",
                    "learned_from": "F1.5",
                    "created": "2026-01-31",
                }
            )
            + "\n"
        )

        # Session that matches (in personal directory)
        (sessions_dir / "index.jsonl").write_text(
            json.dumps(
                {
                    "id": "SES-010",
                    "date": "2026-01-31",
                    "type": "story",
                    "topic": "F1.5 Output Module",
                }
            )
            + "\n"
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # Should have edges
        assert graph.edge_count >= 1


class TestLoadIdentity:
    """Tests for identity extraction from core.yaml."""

    def _write_identity(self, tmp_path: Path) -> None:
        """Create a test identity/core.yaml file."""
        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        identity_dir.mkdir(parents=True)

        (identity_dir / "core.yaml").write_text(
            dedent("""\
            values:
              - number: 1
                name: "Honesty over Agreement"
                description: "Push back on bad ideas"
              - number: 2
                name: "Simplicity over Cleverness"
                description: "Simple solution that works"
              - number: 3
                name: "Observability IS Trust"
                description: "Show work, explain reasoning"
              - number: 4
                name: "Learning over Perfection"
                description: "Every session teaches something"
              - number: 5
                name: "Partnership over Service"
                description: "Collaborator, not tool"

            boundaries:
              will:
                - "Push back on bad ideas"
                - "Stop when I detect incoherence, ambiguity, or drift"
                - "Ask before expensive operations"
                - "Admit uncertainty rather than pretend confidence"
              wont:
                - "Pretend certainty I don't have"
                - "Validate ideas just because they were proposed"
                - "Generate without understanding"
            """)
        )

    def test_extracts_values_as_principle_nodes(self, tmp_path: Path) -> None:
        """Should extract 5 values as principle nodes with always_on=True."""
        self._write_identity(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_identity()

        value_nodes = [n for n in nodes if n.id.startswith("RAI-VAL-")]
        assert len(value_nodes) == 5
        for node in value_nodes:
            assert node.type == "principle"
            assert node.metadata.get("always_on") is True
            assert node.metadata.get("identity_type") == "value"

    def test_extracts_boundaries_as_principle_nodes(self, tmp_path: Path) -> None:
        """Should extract boundaries (I Will + I Won't) as principle nodes."""
        self._write_identity(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_identity()

        boundary_nodes = [n for n in nodes if n.id.startswith("RAI-BND-")]
        assert len(boundary_nodes) >= 4  # At least 4 from I Will
        for node in boundary_nodes:
            assert node.type == "principle"
            assert node.metadata.get("always_on") is True
            assert node.metadata.get("identity_type") == "boundary"

    def test_value_node_content(self, tmp_path: Path) -> None:
        """Value nodes should have 'Title — first bullet' content."""
        self._write_identity(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_identity()

        val1 = next(n for n in nodes if n.id == "RAI-VAL-1")
        assert "Honesty over Agreement" in val1.content

    def test_boundary_node_content(self, tmp_path: Path) -> None:
        """Boundary nodes should have the boundary text as content."""
        self._write_identity(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_identity()

        bnd_nodes = [n for n in nodes if n.id.startswith("RAI-BND-")]
        contents = [n.content for n in bnd_nodes]
        assert any("Stop when I detect incoherence" in c for c in contents)

    def test_returns_empty_when_no_identity_file(self, tmp_path: Path) -> None:
        """Should return empty list when identity/core.yaml doesn't exist."""
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_identity()
        assert nodes == []

    def test_build_includes_identity_nodes(self, tmp_path: Path) -> None:
        """Build should include identity nodes in the graph."""
        self._write_identity(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # Should have value + boundary nodes
        identity_nodes = [
            n
            for n in graph.get_concepts_by_type("principle")
            if n.id.startswith("RAI-")
        ]
        assert len(identity_nodes) >= 5  # At least the 5 values


class TestExtractBoundedContexts:
    """Tests for bounded context extraction from arch-domain-model metadata (S15.2)."""

    def _build_arch_fixtures(self, tmp_path: Path) -> None:
        """Create architecture doc fixtures with domain model and design."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)
        modules_dir = arch_dir / "modules"
        modules_dir.mkdir()

        # Domain model with bounded contexts
        (arch_dir / "domain-model.yaml").write_text(
            dedent("""\
            type: architecture_domain_model
            project: test
            status: current
            bounded_contexts:
              - name: governance
                modules: [governance]
                description: "Extract structured knowledge"
              - name: ontology
                modules: [context, memory]
                description: "Persist and query knowledge"
            shared_kernel:
              modules: [config, core]
              description: "Foundation utilities"
            application_layer:
              modules: [cli]
              description: "Thin orchestration shell"
            distribution:
              modules: [rai_base]
              description: "Packaged content"
            """)
        )

        # System design with layers
        (arch_dir / "system-design.yaml").write_text(
            dedent("""\
            type: architecture_design
            project: test
            status: current
            layers:
              - name: leaf
                modules: [config, core]
                description: "Zero internal dependencies"
              - name: domain
                modules: [governance]
                description: "Independent domain logic"
              - name: integration
                modules: [context, memory]
                description: "Combines domains"
              - name: orchestration
                modules: [cli]
                description: "User-facing entry points"
            """)
        )

        # Module docs (so module nodes exist for edge safety)
        for name in [
            "governance",
            "context",
            "memory",
            "config",
            "core",
            "cli",
            "rai_base",
        ]:
            (modules_dir / f"{name}.yaml").write_text(
                dedent(f"""\
                type: module
                name: {name}
                purpose: "{name} module"
                depends_on: []
                """)
            )

    def test_creates_bounded_context_nodes(self, tmp_path: Path) -> None:
        """Should create bounded_context nodes from domain model metadata."""
        self._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        bc_nodes = graph.get_concepts_by_type("bounded_context")
        bc_ids = {n.id for n in bc_nodes}

        # 2 BCs + shared_kernel + application_layer + distribution = 5
        assert len(bc_nodes) == 5
        assert "bc-governance" in bc_ids
        assert "bc-ontology" in bc_ids
        assert "bc-shared-kernel" in bc_ids
        assert "bc-application-layer" in bc_ids
        assert "bc-distribution" in bc_ids

    def test_bc_nodes_have_correct_content(self, tmp_path: Path) -> None:
        """BC node content should come from the description field."""
        self._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("bc-ontology")
        assert node is not None
        assert node.content == "Persist and query knowledge"
        assert node.metadata.get("bc_type") == "bounded_context"

    def test_shared_kernel_has_bc_type_metadata(self, tmp_path: Path) -> None:
        """Shared kernel should have bc_type='shared_kernel' in metadata."""
        self._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("bc-shared-kernel")
        assert node is not None
        assert node.metadata.get("bc_type") == "shared_kernel"

    def test_creates_belongs_to_edges(self, tmp_path: Path) -> None:
        """Should create belongs_to edges from modules to their BC."""
        self._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # mod-context and mod-memory should belong to bc-ontology
        neighbors = graph.get_neighbors("bc-ontology", edge_types=["belongs_to"])
        neighbor_ids = {n.id for n in neighbors}
        assert "mod-context" in neighbor_ids
        assert "mod-memory" in neighbor_ids

    def test_no_belongs_to_for_missing_modules(self, tmp_path: Path) -> None:
        """Should not create belongs_to edges when module node doesn't exist."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        # Domain model references a module that has no module doc
        (arch_dir / "domain-model.yaml").write_text(
            dedent("""\
            type: architecture_domain_model
            project: test
            status: current
            bounded_contexts:
              - name: phantom
                modules: [nonexistent]
                description: "References missing module"
            shared_kernel:
              modules: []
              description: "Empty"
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # BC node should exist but have no belongs_to neighbors
        node = graph.get_concept("bc-phantom")
        assert node is not None
        neighbors = graph.get_neighbors("bc-phantom", edge_types=["belongs_to"])
        assert len(neighbors) == 0

    def test_graceful_when_no_domain_model(self, tmp_path: Path) -> None:
        """Should produce no BC nodes when arch-domain-model is absent."""
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        bc_nodes = graph.get_concepts_by_type("bounded_context")
        assert len(bc_nodes) == 0


class TestExtractLayers:
    """Tests for layer extraction from arch-design metadata (S15.2)."""

    def test_creates_layer_nodes(self, tmp_path: Path) -> None:
        """Should create layer nodes from system design metadata."""
        # Reuse the fixture builder from TestExtractBoundedContexts
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        layer_nodes = graph.get_concepts_by_type("layer")
        layer_ids = {n.id for n in layer_nodes}

        assert len(layer_nodes) == 4
        assert layer_ids == {
            "lyr-leaf",
            "lyr-domain",
            "lyr-integration",
            "lyr-orchestration",
        }

    def test_layer_nodes_have_correct_content(self, tmp_path: Path) -> None:
        """Layer node content should come from the description field."""
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("lyr-leaf")
        assert node is not None
        assert node.content == "Zero internal dependencies"

    def test_creates_in_layer_edges(self, tmp_path: Path) -> None:
        """Should create in_layer edges from modules to their layer."""
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # mod-context and mod-memory should be in lyr-integration
        neighbors = graph.get_neighbors("lyr-integration", edge_types=["in_layer"])
        neighbor_ids = {n.id for n in neighbors}
        assert "mod-context" in neighbor_ids
        assert "mod-memory" in neighbor_ids

    def test_no_in_layer_for_distribution_modules(self, tmp_path: Path) -> None:
        """Distribution modules (rai_base) should NOT get in_layer edges."""
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # rai_base is in distribution, NOT in any layer
        neighbors = graph.get_neighbors("mod-rai_base", edge_types=["in_layer"])
        assert len(neighbors) == 0

    def test_graceful_when_no_design_doc(self, tmp_path: Path) -> None:
        """Should produce no layer nodes when arch-design is absent."""
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        layer_nodes = graph.get_concepts_by_type("layer")
        assert len(layer_nodes) == 0


class TestExtractConstraints:
    """Tests for constraint edge extraction from guardrail metadata (S15.3)."""

    def _build_constraint_fixtures(self, tmp_path: Path) -> None:
        """Create fixtures with guardrails that have constraint_scope metadata."""
        # Reuse arch fixtures for BCs and layers
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)

        # Create guardrails.md with frontmatter
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir(exist_ok=True)

        (gov_dir / "guardrails.md").write_text(
            dedent("""\
            ---
            type: guardrails
            constraint_scopes:
              default: all_bounded_contexts
              overrides:
                must-arch: [bc-ontology, bc-skills]
                should-cli: [lyr-orchestration]
            ---

            ## Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |

            ### Architecture

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-ARCH-001` | MUST | Engine separation | import analysis | Vision |

            ### CLI Development

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `SHOULD-CLI-001` | SHOULD | Path params | review | Retro |
            """)
        )

    def test_creates_constrained_by_edges_for_universal_scope(
        self, tmp_path: Path
    ) -> None:
        """Universal guardrails (default) create edges to all BCs."""
        self._build_constraint_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # MUST-CODE-001 applies to all BCs (default scope)
        neighbors = graph.get_neighbors("bc-governance", edge_types=["constrained_by"])
        neighbor_ids = {n.id for n in neighbors}
        assert "guardrail-must-code-001" in neighbor_ids

    def test_creates_constrained_by_edges_for_override_scope(
        self, tmp_path: Path
    ) -> None:
        """Override guardrails create edges only to specified targets."""
        self._build_constraint_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # MUST-ARCH-001 applies only to bc-ontology and bc-skills (override)
        onto_neighbors = graph.get_neighbors(
            "bc-ontology", edge_types=["constrained_by"]
        )
        onto_ids = {n.id for n in onto_neighbors}
        assert "guardrail-must-arch-001" in onto_ids

        # bc-governance should NOT have the arch guardrail
        gov_neighbors = graph.get_neighbors(
            "bc-governance", edge_types=["constrained_by"]
        )
        gov_ids = {n.id for n in gov_neighbors}
        assert "guardrail-must-arch-001" not in gov_ids

    def test_creates_constrained_by_edges_for_layer_target(
        self, tmp_path: Path
    ) -> None:
        """Layer-targeted guardrails create edges to layer nodes."""
        self._build_constraint_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # SHOULD-CLI-001 targets lyr-orchestration
        orch_neighbors = graph.get_neighbors(
            "lyr-orchestration", edge_types=["constrained_by"]
        )
        orch_ids = {n.id for n in orch_neighbors}
        assert "guardrail-should-cli-001" in orch_ids

    def test_no_constraint_edges_without_guardrails(self, tmp_path: Path) -> None:
        """No constraint edges when no guardrail nodes exist."""
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        assert graph.edge_count == 0

    def test_no_constraint_edges_without_scope_metadata(self, tmp_path: Path) -> None:
        """Guardrails without constraint_scope metadata produce no constraint edges."""
        # Create arch fixtures (BCs exist)
        TestExtractBoundedContexts()._build_arch_fixtures(tmp_path)

        # Guardrails WITHOUT frontmatter (no constraint_scope in metadata)
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir(exist_ok=True)
        (gov_dir / "guardrails.md").write_text(
            dedent("""\
            ## Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # Guardrail node exists but no constrained_by edges
        node = graph.get_concept("guardrail-must-code-001")
        assert node is not None

        # BCs should have no constrained_by neighbors
        bc_node = graph.get_concept("bc-governance")
        assert bc_node is not None
        neighbors = graph.get_neighbors("bc-governance", edge_types=["constrained_by"])
        assert len(neighbors) == 0

    def test_skips_nonexistent_target_nodes(self, tmp_path: Path) -> None:
        """Should not create edges to nodes that don't exist in graph."""
        arch_dir = tmp_path / "governance" / "architecture"
        arch_dir.mkdir(parents=True)

        # Domain model with a BC that won't have its target in override
        (arch_dir / "domain-model.yaml").write_text(
            dedent("""\
            type: architecture_domain_model
            project: test
            status: current
            bounded_contexts:
              - name: governance
                modules: []
                description: "Test BC"
            shared_kernel:
              modules: []
              description: "Empty"
            """)
        )

        gov_dir = tmp_path / "governance"
        gov_dir.mkdir(exist_ok=True)
        (gov_dir / "guardrails.md").write_text(
            dedent("""\
            ---
            type: guardrails
            constraint_scopes:
              default: all_bounded_contexts
              overrides:
                must-arch: [bc-nonexistent]
            ---

            ## Guardrails

            ### Architecture

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-ARCH-001` | MUST | Engine separation | import | Vision |
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # bc-nonexistent doesn't exist, so no constrained_by edges for must-arch
        # bc-governance exists and should NOT have must-arch (it's overridden)
        neighbors = graph.get_neighbors("bc-governance", edge_types=["constrained_by"])
        arch_neighbors = [n for n in neighbors if "arch" in n.id]
        assert len(arch_neighbors) == 0


class TestLoadCodeStructure:
    """Tests for code structure integration (S16.1)."""

    def _build_code_fixtures(self, tmp_path: Path) -> None:
        """Create module docs + matching source code."""
        # Module docs (frontmatter)
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)

        (modules_dir / "alpha.yaml").write_text(
            dedent("""\
            type: module
            name: alpha
            purpose: "Alpha module"
            depends_on: [beta]
            components: 10
            """)
        )
        (modules_dir / "beta.yaml").write_text(
            dedent("""\
            type: module
            name: beta
            purpose: "Beta module"
            depends_on: []
            components: 5
            """)
        )

        # Source code
        src_dir = tmp_path / "src" / "raise_cli"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text(
            dedent("""\
            from raise_cli.alpha.core import Foo

            __all__ = ["Foo"]
            """)
        )
        (alpha / "core.py").write_text(
            dedent("""\
            from raise_cli.beta import helper

            class Foo:
                pass

            def do_stuff():
                pass
            """)
        )

        beta = src_dir / "beta"
        beta.mkdir(parents=True)
        (beta / "__init__.py").write_text(
            dedent("""\
            from raise_cli.beta.utils import helper

            __all__ = ["helper"]
            """)
        )
        (beta / "utils.py").write_text(
            dedent("""\
            def helper():
                pass
            """)
        )

        # pyproject.toml so PythonAnalyzer.detect() works
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

    def test_enriches_module_nodes_with_code_imports(self, tmp_path: Path) -> None:
        """Module nodes should gain code_imports metadata from ast analysis."""
        self._build_code_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("mod-alpha")
        assert node is not None
        assert "code_imports" in node.metadata
        assert "beta" in node.metadata["code_imports"]

    def test_enriches_module_nodes_with_code_exports(self, tmp_path: Path) -> None:
        """Module nodes should gain code_exports metadata from __init__.py."""
        self._build_code_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("mod-alpha")
        assert node is not None
        assert "code_exports" in node.metadata
        assert "Foo" in node.metadata["code_exports"]

    def test_enriches_module_nodes_with_code_components(self, tmp_path: Path) -> None:
        """Module nodes should gain code_components count from ast."""
        self._build_code_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("mod-alpha")
        assert node is not None
        assert "code_components" in node.metadata
        # Foo class + do_stuff function = 2
        assert node.metadata["code_components"] == 2

    def test_preserves_frontmatter_data(self, tmp_path: Path) -> None:
        """Existing frontmatter fields (depends_on, components) should be preserved."""
        self._build_code_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("mod-alpha")
        assert node is not None
        # Frontmatter data still there
        assert node.metadata["depends_on"] == ["beta"]
        assert node.metadata["components"] == 10
        # Code data added alongside
        assert "code_imports" in node.metadata

    def test_modules_without_source_retain_existing_data(self, tmp_path: Path) -> None:
        """Module nodes without matching source should keep their data unchanged."""
        # Module doc exists but no source code for it
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)
        (modules_dir / "orphan.yaml").write_text(
            dedent("""\
            type: module
            name: orphan
            purpose: "No source code"
            depends_on: []
            """)
        )

        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        # Create empty src dir so analyzer runs but finds no modules
        (tmp_path / "src" / "raise_cli").mkdir(parents=True)

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        node = graph.get_concept("mod-orphan")
        assert node is not None
        # No code_ keys added
        assert "code_imports" not in node.metadata

    def test_graceful_when_no_python_project(self, tmp_path: Path) -> None:
        """Should not crash when project has no pyproject.toml."""
        modules_dir = tmp_path / "governance" / "architecture" / "modules"
        modules_dir.mkdir(parents=True)
        (modules_dir / "core.yaml").write_text(
            dedent("""\
            type: module
            name: core
            purpose: "Core module"
            depends_on: []
            """)
        )

        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
        ):
            graph = builder.build()

        # mod-core should exist from frontmatter, no code data
        node = graph.get_concept("mod-core")
        assert node is not None
        assert "code_imports" not in node.metadata

    def test_build_calls_load_code_structure(self, tmp_path: Path) -> None:
        """build() should call load_code_structure() in its pipeline."""
        self._build_code_fixtures(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)

        with (
            patch.object(builder, "load_governance", return_value=[]),
            patch.object(builder, "load_memory", return_value=[]),
            patch.object(builder, "load_skills", return_value=[]),
            patch.object(builder, "load_components", return_value=[]),
            patch.object(
                builder, "load_code_structure", wraps=builder.load_code_structure
            ) as mock_code,
        ):
            builder.build()

        mock_code.assert_called_once()


class TestRaiBaseTemplateContract:
    """Contract tests: rai_base architecture templates produce valid graph nodes.

    These tests verify PAT-202/203 (templates-as-contract): the bundled
    templates in rai_base MUST parse through _parse_architecture_doc and
    produce non-None nodes.
    """

    def _get_rai_base_arch_dir(self) -> Path:
        """Get the path to bundled rai_base architecture templates."""
        from importlib.resources import files as pkg_files

        base = pkg_files("raise_cli.rai_base") / "governance" / "architecture"
        # importlib Traversable → Path
        return Path(str(base))

    def test_system_context_template_produces_node(self, tmp_path: Path) -> None:
        """system-context.yaml template must parse into arch-context node."""
        src = self._get_rai_base_arch_dir() / "system-context.yaml"
        content = src.read_text(encoding="utf-8").replace(
            "{project_name}", "test-project"
        )

        dest_dir = tmp_path / "governance" / "architecture"
        dest_dir.mkdir(parents=True)
        (dest_dir / "system-context.yaml").write_text(content)

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.id == "arch-context"]
        assert len(arch_nodes) == 1, (
            "system-context.yaml must produce arch-context node"
        )
        assert arch_nodes[0].type == "architecture"
        assert arch_nodes[0].metadata["arch_type"] == "architecture_context"

    def test_system_design_template_produces_node(self, tmp_path: Path) -> None:
        """system-design.yaml template must parse into arch-design node."""
        src = self._get_rai_base_arch_dir() / "system-design.yaml"
        content = src.read_text(encoding="utf-8").replace(
            "{project_name}", "test-project"
        )

        dest_dir = tmp_path / "governance" / "architecture"
        dest_dir.mkdir(parents=True)
        (dest_dir / "system-design.yaml").write_text(content)

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.id == "arch-design"]
        assert len(arch_nodes) == 1, "system-design.yaml must produce arch-design node"
        assert arch_nodes[0].type == "architecture"
        assert arch_nodes[0].metadata["arch_type"] == "architecture_design"

    def test_domain_model_template_produces_node(self, tmp_path: Path) -> None:
        """domain-model.yaml template must parse into arch-domain-model node."""
        src = self._get_rai_base_arch_dir() / "domain-model.yaml"
        content = src.read_text(encoding="utf-8").replace(
            "{project_name}", "test-project"
        )

        dest_dir = tmp_path / "governance" / "architecture"
        dest_dir.mkdir(parents=True)
        (dest_dir / "domain-model.yaml").write_text(content)

        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_architecture()

        arch_nodes = [n for n in nodes if n.id == "arch-domain-model"]
        assert len(arch_nodes) == 1, (
            "domain-model.yaml must produce arch-domain-model node"
        )
        assert arch_nodes[0].type == "architecture"
        assert arch_nodes[0].metadata["arch_type"] == "architecture_domain_model"

    def test_all_architecture_templates_have_type_field(self) -> None:
        """Every .yaml file in rai_base architecture dir must have type: field."""
        arch_dir = self._get_rai_base_arch_dir()
        yaml_files = list(arch_dir.glob("*.yaml"))

        assert len(yaml_files) >= 3, (
            f"Expected >=3 architecture templates, found {len(yaml_files)}: {yaml_files}"
        )

        for yaml_file in yaml_files:
            content = yaml_file.read_text(encoding="utf-8")
            assert "type:" in content, f"{yaml_file.name} must contain 'type:' field"
