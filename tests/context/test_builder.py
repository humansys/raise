"""Tests for UnifiedGraphBuilder."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.context.builder import UnifiedGraphBuilder
from raise_cli.context.models import ConceptNode
from raise_cli.memory.models import MemoryScope


class TestUnifiedGraphBuilderInit:
    """Tests for UnifiedGraphBuilder initialization."""

    def test_initializes_with_project_root(self, tmp_path: Path) -> None:
        """Should accept project root path."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)
        assert builder.project_root == tmp_path

    def test_uses_cwd_when_no_root_provided(self) -> None:
        """Should use current directory when no root provided."""
        builder = UnifiedGraphBuilder()
        assert builder.project_root == Path.cwd()


class TestLoadGovernance:
    """Tests for load_governance method."""

    def test_converts_concepts_to_nodes(self, tmp_path: Path) -> None:
        """Should convert governance Concept to ConceptNode."""
        # Create mock concept
        from raise_cli.governance.models import Concept, ConceptType

        mock_concept = Concept(
            id="principle-1",
            type=ConceptType.PRINCIPLE,
            file="framework/reference/constitution.md",
            section="§1 Core Principle",
            lines=(10, 20),
            content="This is a core principle.",
            metadata={"principle_number": "§1"},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "_get_governance_extractor") as mock_extractor:
            mock_extractor.return_value.extract_all.return_value = [mock_concept]
            nodes = builder.load_governance()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "principle-1"
        assert node.type == "principle"
        assert node.content == "This is a core principle."
        assert node.source_file == "framework/reference/constitution.md"

    def test_handles_empty_extraction(self, tmp_path: Path) -> None:
        """Should return empty list when no concepts extracted."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)

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
            json.dumps({
                "id": "PAT-001",
                "type": "codebase",
                "content": "Singleton pattern for testing",
                "context": ["testing", "patterns"],
                "created": "2026-01-31",
            })
            + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "CAL-001",
                "feature": "F1.1",
                "name": "Project Scaffolding",
                "size": "S",
                "sp": 3,
                "actual_min": 30,
                "created": "2026-01-31",
            })
            + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "SES-001",
                "date": "2026-02-01",
                "type": "feature",
                "topic": "E3 Implementation",
                "outcomes": ["Feature complete", "Tests passing"],
            })
            + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "SES-001"
        assert node.type == "session"
        assert "E3 Implementation" in node.content

    def test_handles_missing_memory_directory(self, tmp_path: Path) -> None:
        """Should return empty list if .raise/rai/memory doesn't exist."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({"id": "PAT-001", "type": "process", "content": "Pattern", "created": "2026-01-31"}) + "\n"
        )
        (memory_dir / "calibration.jsonl").write_text(
            json.dumps({"id": "CAL-001", "feature": "F1.1", "name": "Test", "created": "2026-01-31"}) + "\n"
        )
        (sessions_dir / "index.jsonl").write_text(
            json.dumps({"id": "SES-001", "date": "2026-02-01", "topic": "Session"}) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        assert len(nodes) == 3
        types = {n.type for n in nodes}
        assert types == {"pattern", "calibration", "session"}


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
            json.dumps({
                "id": "PAT-GLOBAL",
                "type": "universal",
                "content": "Universal pattern",
                "created": "2026-01-31",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-PROJECT",
                "type": "codebase",
                "content": "Project pattern",
                "created": "2026-01-31",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-PERSONAL",
                "type": "process",
                "content": "Personal pattern",
                "created": "2026-01-31",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({"id": "PAT-G1", "type": "universal", "content": "Global", "created": "2026-01-31"}) + "\n"
        )

        # Setup project
        project_memory = tmp_path / ".raise/rai" / "memory"
        project_memory.mkdir(parents=True)
        (project_memory / "patterns.jsonl").write_text(
            json.dumps({"id": "PAT-P1", "type": "codebase", "content": "Project", "created": "2026-01-31"}) + "\n"
        )

        # Setup personal
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps({"id": "PAT-L1", "type": "process", "content": "Personal", "created": "2026-01-31"}) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "CAL-GLOBAL",
                "feature": "F1.1",
                "name": "Global Cal",
                "size": "S",
                "created": "2026-01-31",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({"id": "SES-PROJECT", "date": "2026-02-01", "type": "feature", "topic": "Project session"}) + "\n"
        )

        # Personal sessions (SHOULD be loaded)
        personal_sessions = tmp_path / ".raise/rai" / "personal" / "sessions"
        personal_sessions.mkdir(parents=True)
        (personal_sessions / "index.jsonl").write_text(
            json.dumps({"id": "SES-PERSONAL", "date": "2026-02-01", "type": "feature", "topic": "Personal session"}) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-001",
                "type": "codebase",
                "content": "Project version",
                "created": "2026-01-31",
            }) + "\n"
        )

        # Personal pattern with same ID
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps({
                "id": "PAT-001",
                "type": "codebase",
                "content": "Personal override",
                "created": "2026-02-01",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-002",
                "type": "universal",
                "content": "Global version",
                "created": "2026-01-30",
            }) + "\n"
        )

        # Project pattern with same ID
        project_dir = tmp_path / ".raise/rai" / "memory"
        project_dir.mkdir(parents=True)
        (project_dir / "patterns.jsonl").write_text(
            json.dumps({
                "id": "PAT-002",
                "type": "codebase",
                "content": "Project override",
                "created": "2026-01-31",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-003",
                "type": "universal",
                "content": "Global version",
                "created": "2026-01-30",
            }) + "\n"
        )

        # Personal pattern with same ID (skipping project)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps({
                "id": "PAT-003",
                "type": "process",
                "content": "Personal override",
                "created": "2026-02-01",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({"id": "PAT-G1", "type": "universal", "content": "Global", "created": "2026-01-30"}) + "\n"
        )

        # Project pattern (different ID)
        project_dir = tmp_path / ".raise/rai" / "memory"
        project_dir.mkdir(parents=True)
        (project_dir / "patterns.jsonl").write_text(
            json.dumps({"id": "PAT-P1", "type": "codebase", "content": "Project", "created": "2026-01-31"}) + "\n"
        )

        # Personal pattern (different ID)
        personal_dir = tmp_path / ".raise/rai" / "personal"
        personal_dir.mkdir(parents=True)
        (personal_dir / "patterns.jsonl").write_text(
            json.dumps({"id": "PAT-L1", "type": "process", "content": "Personal", "created": "2026-02-01"}) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_memory()

        # All three should be preserved
        assert len(nodes) == 3
        ids = {n.id for n in nodes}
        assert ids == {"PAT-G1", "PAT-P1", "PAT-L1"}


class TestLoadWork:
    """Tests for load_work method."""

    def test_converts_epics_to_nodes(self, tmp_path: Path) -> None:
        """Should convert epic Concept to ConceptNode."""
        from raise_cli.governance.models import Concept, ConceptType

        mock_epic = Concept(
            id="E11",
            type=ConceptType.EPIC,
            file="governance/projects/raise-cli/backlog.md",
            section="E11: Unified Context",
            lines=(50, 60),
            content="Unified context architecture epic",
            metadata={"status": "In Progress"},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "_extract_epics") as mock_extract:
            mock_extract.return_value = [mock_epic]
            with patch.object(builder, "_extract_features") as mock_features:
                mock_features.return_value = []
                nodes = builder.load_work()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "E11"
        assert node.type == "epic"

    def test_converts_features_to_nodes(self, tmp_path: Path) -> None:
        """Should convert feature Concept to ConceptNode."""
        from raise_cli.governance.models import Concept, ConceptType

        mock_feature = Concept(
            id="F11.2",
            type=ConceptType.FEATURE,
            file="dev/epic-e11-scope.md",
            section="F11.2: Graph Builder",
            lines=(70, 80),
            content="Build unified graph from sources",
            metadata={"size": "M", "status": "Pending"},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "_extract_epics") as mock_epics:
            mock_epics.return_value = []
            with patch.object(builder, "_extract_features") as mock_extract:
                mock_extract.return_value = [mock_feature]
                nodes = builder.load_work()

        assert len(nodes) == 1
        node = nodes[0]
        assert node.id == "F11.2"
        assert node.type == "feature"


class TestLoadSkills:
    """Tests for load_skills method."""

    def test_loads_skills_from_directory(self, tmp_path: Path) -> None:
        """Should load skills from .claude/skills directory."""
        skills_dir = tmp_path / ".claude" / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)

        (skills_dir / "SKILL.md").write_text(dedent("""\
            ---
            name: test-skill
            description: A test skill
            ---
            # Test
        """))

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_skills()

        assert len(nodes) == 1
        assert nodes[0].id == "/test-skill"
        assert nodes[0].type == "skill"

    def test_handles_missing_skills_directory(self, tmp_path: Path) -> None:
        """Should return empty list if .claude/skills doesn't exist."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_skills()

        assert nodes == []


class TestLoadComponents:
    """Tests for load_components method."""

    def test_loads_components_from_validated_json(self, tmp_path: Path) -> None:
        """Should load components from components-validated.json."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(json.dumps({
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
        }))

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert len(nodes) == 2
        assert nodes[0].id == "comp-scanner-symbol"
        assert nodes[0].type == "component"
        assert nodes[0].content == "Core data model for code symbols"
        assert nodes[0].metadata.get("name") == "Symbol"
        assert nodes[0].metadata.get("category") == "model"

    def test_handles_missing_components_file(self, tmp_path: Path) -> None:
        """Should return empty list if components-validated.json doesn't exist."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []

    def test_handles_empty_components_list(self, tmp_path: Path) -> None:
        """Should return empty list if components array is empty."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(json.dumps({
            "generated_at": "2026-02-04T12:10:00Z",
            "components": [],
        }))

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []

    def test_handles_invalid_json(self, tmp_path: Path) -> None:
        """Should return empty list on invalid JSON."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text("not valid json")

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        nodes = builder.load_components()

        assert nodes == []


class TestBuild:
    """Tests for build method."""

    def test_builds_graph_with_all_sources(self, tmp_path: Path) -> None:
        """Should combine all sources into UnifiedGraph."""
        # Setup minimal fixtures
        memory_dir = tmp_path / ".raise/rai" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "patterns.jsonl").write_text(
            json.dumps({"id": "PAT-001", "type": "process", "content": "Test", "created": "2026-01-31"}) + "\n"
        )

        skills_dir = tmp_path / ".claude" / "skills" / "test"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(dedent("""\
            ---
            name: test
            description: Test skill
            ---
            # Test
        """))

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        # Mock governance, work, and components loaders
        with patch.object(builder, "load_governance") as mock_gov:
            mock_gov.return_value = []
            with patch.object(builder, "load_work") as mock_work:
                mock_work.return_value = []
                with patch.object(builder, "load_components") as mock_comp:
                    mock_comp.return_value = []
                    graph = builder.build()

        # Should have memory + skills
        assert graph.node_count >= 2

    def test_build_returns_unified_graph(self, tmp_path: Path) -> None:
        """Should return UnifiedGraph instance."""
        from raise_cli.context.graph import UnifiedGraph

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "load_governance", return_value=[]):
            with patch.object(builder, "load_memory", return_value=[]):
                with patch.object(builder, "load_work", return_value=[]):
                    with patch.object(builder, "load_skills", return_value=[]):
                        with patch.object(builder, "load_components", return_value=[]):
                            graph = builder.build()

        assert isinstance(graph, UnifiedGraph)

    def test_build_includes_components(self, tmp_path: Path) -> None:
        """Should include components in the built graph."""
        # Setup components file
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(json.dumps({
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
        }))

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "load_governance", return_value=[]):
            with patch.object(builder, "load_memory", return_value=[]):
                with patch.object(builder, "load_work", return_value=[]):
                    with patch.object(builder, "load_skills", return_value=[]):
                        graph = builder.build()

        assert graph.node_count == 1
        node = graph.get_concept("comp-test")
        assert node is not None
        assert node.type == "component"
        assert node.content == "Test component"


class TestInferRelationships:
    """Tests for infer_relationships method."""

    def test_infers_learned_from_edges(self, tmp_path: Path) -> None:
        """Should create learned_from edges from pattern.learned_from field."""
        pattern = ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"learned_from": "F1.5"},
        )
        session = ConceptNode(
            id="SES-010",
            type="session",
            content="F1.5 session",
            source_file=".raise/rai/memory/sessions/index.jsonl",
            created="2026-01-31",
            metadata={"topic": "F1.5 Output Module"},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([pattern, session])

        learned_edges = [e for e in edges if e.type == "learned_from"]
        assert len(learned_edges) >= 1
        edge = learned_edges[0]
        assert edge.source == "PAT-001"
        assert edge.weight == 1.0

    def test_infers_part_of_edges(self, tmp_path: Path) -> None:
        """Should create part_of edges from feature to epic."""
        feature = ConceptNode(
            id="F11.2",
            type="feature",
            content="Graph Builder",
            source_file="dev/epic-e11-scope.md",
            created="2026-02-03",
            metadata={},
        )
        epic = ConceptNode(
            id="E11",
            type="epic",
            content="Unified Context",
            source_file="governance/projects/raise-cli/backlog.md",
            created="2026-02-03",
            metadata={},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([feature, epic])

        part_of_edges = [e for e in edges if e.type == "part_of"]
        assert len(part_of_edges) == 1
        assert part_of_edges[0].source == "F11.2"
        assert part_of_edges[0].target == "E11"
        assert part_of_edges[0].weight == 1.0

    def test_infers_skill_prerequisite_edges(self, tmp_path: Path) -> None:
        """Should create needs_context edges from skill prerequisites."""
        skill = ConceptNode(
            id="/feature-plan",
            type="skill",
            content="Plan implementation tasks",
            source_file=".claude/skills/feature-plan/SKILL.md",
            created="2026-02-03",
            metadata={"raise.prerequisites": "project-backlog"},
        )
        prereq = ConceptNode(
            id="/project-backlog",
            type="skill",
            content="Manage project backlog",
            source_file=".claude/skills/project-backlog/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([skill, prereq])

        needs_edges = [e for e in edges if e.type == "needs_context"]
        assert len(needs_edges) == 1
        assert needs_edges[0].source == "/feature-plan"
        assert needs_edges[0].target == "/project-backlog"
        assert needs_edges[0].weight == 1.0

    def test_infers_skill_next_edges(self, tmp_path: Path) -> None:
        """Should create related_to edges from skill.raise/raise.next."""
        skill = ConceptNode(
            id="/feature-plan",
            type="skill",
            content="Plan tasks",
            source_file=".claude/skills/feature-plan/SKILL.md",
            created="2026-02-03",
            metadata={"raise.next": "feature-implement"},
        )
        next_skill = ConceptNode(
            id="/feature-implement",
            type="skill",
            content="Implement feature",
            source_file=".claude/skills/feature-implement/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([skill, next_skill])

        next_edges = [e for e in edges if e.source == "/feature-plan" and e.target == "/feature-implement"]
        assert len(next_edges) == 1
        assert next_edges[0].type == "related_to"
        assert next_edges[0].weight == 1.0

    def test_infers_related_to_by_shared_keywords(self, tmp_path: Path) -> None:
        """Should create related_to edges for concepts with shared keywords."""
        pattern = ConceptNode(
            id="PAT-012",
            type="pattern",
            content="Design-first eliminates ambiguity in implementation planning",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"context": ["planning", "implementation"]},
        )
        skill = ConceptNode(
            id="/feature-plan",
            type="skill",
            content="Planning implementation tasks for feature development",
            source_file=".claude/skills/feature-plan/SKILL.md",
            created="2026-02-03",
            metadata={},
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)
        edges = builder.infer_relationships([pattern, skill])

        related_edges = [e for e in edges if e.type == "related_to"]
        # Should find shared keywords "planning" and "implementation"
        assert len(related_edges) >= 1
        # Inferred edges have weight < 1.0
        inferred = [e for e in related_edges if e.weight < 1.0]
        assert len(inferred) >= 1

    def test_returns_empty_for_no_nodes(self, tmp_path: Path) -> None:
        """Should return empty list when no nodes provided."""
        builder = UnifiedGraphBuilder(project_root=tmp_path)
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
            json.dumps({
                "id": "PAT-001",
                "type": "process",
                "content": "Test pattern",
                "learned_from": "F1.5",
                "created": "2026-01-31",
            }) + "\n"
        )

        # Session that matches (in personal directory)
        (sessions_dir / "index.jsonl").write_text(
            json.dumps({
                "id": "SES-010",
                "date": "2026-01-31",
                "type": "feature",
                "topic": "F1.5 Output Module",
            }) + "\n"
        )

        builder = UnifiedGraphBuilder(project_root=tmp_path)

        with patch.object(builder, "load_governance", return_value=[]):
            with patch.object(builder, "load_work", return_value=[]):
                with patch.object(builder, "load_skills", return_value=[]):
                    with patch.object(builder, "load_components", return_value=[]):
                        graph = builder.build()

        # Should have edges
        assert graph.edge_count >= 1
