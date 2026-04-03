"""Tests for retrieval + prompting config in DomainManifest."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

from rai_agent.knowledge.domain import (
    DomainConfigError,
    load_domain,
    resolve_adapter,
    resolve_builder,
)

if TYPE_CHECKING:
    from pathlib import Path


def _scaleup_available() -> bool:
    try:
        import rai_agent.scaleup  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


def _write_domain_yaml(domain_dir: Path, data: dict[str, object]) -> None:
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "extracted").mkdir(exist_ok=True)
    (domain_dir / "curated").mkdir(exist_ok=True)
    (domain_dir / "domain.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True)
    )


def _base_manifest() -> dict[str, object]:
    return {
        "name": "test",
        "display_name": "Test",
        "schema": {
            "module": "tests.knowledge.conftest",
            "class_name": "SampleNode",
        },
    }


class TestRetrievalConfig:
    """DomainManifest loads retrieval.adapter and retrieval.builder from domain.yaml."""

    def test_manifest_with_retrieval_config(self, tmp_path: Path) -> None:
        data = _base_manifest()
        data["retrieval"] = {
            "adapter": {
                "module": "rai_agent.scaleup.retrieval.adapter",
                "class_name": "ScaleUpAdapter",
            },
            "builder": {
                "module": "rai_agent.scaleup.graph.builder",
                "class_name": "ScaleUpGraphBuilder",
            },
        }
        _write_domain_yaml(tmp_path / "dom", data)

        manifest, _ = load_domain(tmp_path / "dom")
        assert manifest.retrieval is not None
        adapter_mod = "rai_agent.scaleup.retrieval.adapter"
        assert manifest.retrieval.adapter.module == adapter_mod
        assert manifest.retrieval.adapter.class_name == "ScaleUpAdapter"
        assert manifest.retrieval.builder.module == "rai_agent.scaleup.graph.builder"
        assert manifest.retrieval.builder.class_name == "ScaleUpGraphBuilder"

    def test_manifest_without_retrieval_is_none(self, tmp_path: Path) -> None:
        data = _base_manifest()
        _write_domain_yaml(tmp_path / "dom", data)

        manifest, _ = load_domain(tmp_path / "dom")
        assert manifest.retrieval is None


class TestPromptingConfig:
    """DomainManifest loads prompting.system_context and response_format."""

    def test_manifest_with_prompting(self, tmp_path: Path) -> None:
        data = _base_manifest()
        data["prompting"] = {
            "system_context": "You are an expert.",
            "response_format": "1. Diagnosis\n2. Tools\n3. Next step",
        }
        _write_domain_yaml(tmp_path / "dom", data)

        manifest, _ = load_domain(tmp_path / "dom")
        assert manifest.prompting is not None
        assert manifest.prompting.system_context == "You are an expert."
        assert "Diagnosis" in manifest.prompting.response_format

    def test_manifest_without_prompting_is_none(self, tmp_path: Path) -> None:
        data = _base_manifest()
        _write_domain_yaml(tmp_path / "dom", data)

        manifest, _ = load_domain(tmp_path / "dom")
        assert manifest.prompting is None


class TestResolveAdapter:
    """resolve_adapter() dynamically imports the adapter class."""

    @pytest.mark.skipif(
        not _scaleup_available(),
        reason="rai_agent.scaleup not available (private module)",
    )
    def test_resolve_scaleup_adapter(self, tmp_path: Path) -> None:
        data = _base_manifest()
        data["retrieval"] = {
            "adapter": {
                "module": "rai_agent.scaleup.retrieval.adapter",
                "class_name": "ScaleUpAdapter",
            },
            "builder": {
                "module": "rai_agent.scaleup.graph.builder",
                "class_name": "ScaleUpGraphBuilder",
            },
        }
        _write_domain_yaml(tmp_path / "dom", data)
        manifest, _ = load_domain(tmp_path / "dom")

        adapter = resolve_adapter(manifest)
        # Should be an instance implementing DomainAdapter protocol
        assert hasattr(adapter, "interpret_query")
        assert hasattr(adapter, "advise_traversal")
        assert hasattr(adapter, "annotate_results")

    def test_resolve_adapter_bad_module(self, tmp_path: Path) -> None:
        data = _base_manifest()
        data["retrieval"] = {
            "adapter": {
                "module": "nonexistent.module",
                "class_name": "Nope",
            },
            "builder": {
                "module": "tests.knowledge.conftest",
                "class_name": "SampleNode",
            },
        }
        _write_domain_yaml(tmp_path / "dom", data)
        manifest, _ = load_domain(tmp_path / "dom")

        with pytest.raises(DomainConfigError, match="Cannot import"):
            resolve_adapter(manifest)

    def test_resolve_adapter_no_retrieval(self, tmp_path: Path) -> None:
        data = _base_manifest()
        _write_domain_yaml(tmp_path / "dom", data)
        manifest, _ = load_domain(tmp_path / "dom")

        with pytest.raises(DomainConfigError, match="No retrieval config"):
            resolve_adapter(manifest)


class TestResolveBuilder:
    """resolve_builder() dynamically imports the builder class."""

    @pytest.mark.skipif(
        not _scaleup_available(),
        reason="rai_agent.scaleup not available (private module)",
    )
    def test_resolve_scaleup_builder(self, tmp_path: Path) -> None:
        data = _base_manifest()
        data["retrieval"] = {
            "adapter": {
                "module": "rai_agent.scaleup.retrieval.adapter",
                "class_name": "ScaleUpAdapter",
            },
            "builder": {
                "module": "rai_agent.scaleup.graph.builder",
                "class_name": "ScaleUpGraphBuilder",
            },
        }
        _write_domain_yaml(tmp_path / "dom", data)
        manifest, _ = load_domain(tmp_path / "dom")

        builder = resolve_builder(manifest)
        assert hasattr(builder, "build_from_directory")

    def test_resolve_builder_no_retrieval(self, tmp_path: Path) -> None:
        data = _base_manifest()
        _write_domain_yaml(tmp_path / "dom", data)
        manifest, _ = load_domain(tmp_path / "dom")

        with pytest.raises(DomainConfigError, match="No retrieval config"):
            resolve_builder(manifest)
