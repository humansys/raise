"""Tests for domain loading, discovery, and scaffolding."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

import pytest
import yaml
from tests.knowledge.conftest import SampleNode

from rai_agent.knowledge.domain import (
    DomainConfigError,
    discover_domains,
    load_domain,
    scaffold_domain,
)


class TestLoadDomain:
    def test_load_valid_domain(self, sample_domain_dir: Path) -> None:
        manifest, config = load_domain(sample_domain_dir)
        assert manifest.name == "test"
        assert manifest.display_name == "Test Domain"
        assert config.node_model is SampleNode
        assert config.cq_threshold == 80.0
        # curated/ is empty, extracted/ has files → uses extracted/
        assert config.node_dir == sample_domain_dir / "extracted"

    def test_load_uses_extracted_if_no_curated(self, tmp_path: Path) -> None:
        """If curated/ is empty but extracted/ has files, use extracted/."""
        domain_dir = tmp_path / "dom"
        domain_dir.mkdir()
        manifest_data = {
            "name": "test",
            "display_name": "Test",
            "schema": {
                "module": "tests.knowledge.conftest",
                "class_name": "SampleNode",
            },
        }
        (domain_dir / "domain.yaml").write_text(
            yaml.dump(manifest_data, default_flow_style=False)
        )
        extracted = domain_dir / "extracted"
        extracted.mkdir()
        (extracted / "node.yaml").write_text("id: n1\ntype: t\nname: n\nsummary: s\n")
        (domain_dir / "curated").mkdir()  # empty

        _, config = load_domain(domain_dir)
        # curated is empty, so node_dir falls back to extracted
        assert config.node_dir == extracted

    def test_load_missing_domain_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(DomainConfigError, match="domain.yaml not found"):
            load_domain(tmp_path)

    def test_load_bad_schema_module(self, tmp_path: Path) -> None:
        domain_dir = tmp_path / "bad"
        domain_dir.mkdir()
        manifest_data = {
            "name": "bad",
            "display_name": "Bad",
            "schema": {
                "module": "nonexistent.module.that.doesnt.exist",
                "class_name": "Nope",
            },
        }
        (domain_dir / "domain.yaml").write_text(
            yaml.dump(manifest_data, default_flow_style=False)
        )
        with pytest.raises(DomainConfigError, match="Cannot import"):
            load_domain(domain_dir)

    def test_load_class_not_basemodel(self, tmp_path: Path) -> None:
        domain_dir = tmp_path / "notmodel"
        domain_dir.mkdir()
        manifest_data = {
            "name": "notmodel",
            "display_name": "Not Model",
            "schema": {
                "module": "pathlib",
                "class_name": "Path",
            },
        }
        (domain_dir / "domain.yaml").write_text(
            yaml.dump(manifest_data, default_flow_style=False)
        )
        with pytest.raises(DomainConfigError, match="not a Pydantic BaseModel"):
            load_domain(domain_dir)


class TestDiscoverDomains:
    def test_discover_finds_domains(self, tmp_path: Path) -> None:
        # Create two domain dirs
        for name in ["alpha", "beta"]:
            d = tmp_path / name
            d.mkdir()
            manifest = {
                "name": name,
                "display_name": name.title(),
                "schema": {
                    "module": "tests.knowledge.conftest",
                    "class_name": "SampleNode",
                },
            }
            (d / "domain.yaml").write_text(
                yaml.dump(manifest, default_flow_style=False)
            )

        domains = discover_domains(tmp_path)
        names = [m.name for m, _ in domains]
        assert "alpha" in names
        assert "beta" in names

    def test_discover_skips_invalid(self, tmp_path: Path) -> None:
        # Valid domain
        good = tmp_path / "good"
        good.mkdir()
        (good / "domain.yaml").write_text(
            yaml.dump(
                {
                    "name": "good",
                    "display_name": "Good",
                    "schema": {
                        "module": "tests.knowledge.conftest",
                        "class_name": "SampleNode",
                    },
                },
                default_flow_style=False,
            )
        )
        # Invalid domain (no domain.yaml)
        bad = tmp_path / "bad"
        bad.mkdir()

        domains = discover_domains(tmp_path)
        assert len(domains) == 1
        assert domains[0][0].name == "good"

    def test_discover_empty(self, tmp_path: Path) -> None:
        domains = discover_domains(tmp_path)
        assert domains == []


class TestScaffoldDomain:
    def test_scaffold_creates_structure(self, tmp_path: Path) -> None:
        domain_dir = scaffold_domain(
            base_dir=tmp_path,
            domain_name="gtd",
            corpus_paths=["~/Books/gtd.md"],
        )
        assert domain_dir.exists()
        assert (domain_dir / "domain.yaml").exists()
        assert (domain_dir / "extracted").is_dir()
        assert (domain_dir / "curated").is_dir()

        # Check manifest content
        manifest = yaml.safe_load((domain_dir / "domain.yaml").read_text())
        assert manifest["name"] == "gtd"
        assert manifest["corpus"] == ["~/Books/gtd.md"]
        assert manifest["schema"]["module"] == "TODO"

    def test_scaffold_already_exists(self, tmp_path: Path) -> None:
        (tmp_path / "existing").mkdir()
        (tmp_path / "existing" / "domain.yaml").write_text("name: existing")

        with pytest.raises(DomainConfigError, match="already exists"):
            scaffold_domain(base_dir=tmp_path, domain_name="existing")
