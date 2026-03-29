"""Tests for RAISE-1060: adapter models restructure.

Validates that models are split by protocol concern and filesystem
internals are extracted from the shared boundary models package.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel


class TestPerProtocolModules:
    """Models are organized into per-protocol submodules."""

    def test_pm_models_importable_from_submodule(self) -> None:
        from raise_cli.adapters.models.pm import (
            BatchResult,
            Comment,
            CommentRef,
            FailureDetail,
            IssueDetail,
            IssueRef,
            IssueSpec,
            IssueSummary,
        )

        assert issubclass(IssueSpec, BaseModel)
        assert issubclass(IssueRef, BaseModel)
        assert issubclass(IssueDetail, BaseModel)
        assert issubclass(IssueSummary, BaseModel)
        assert issubclass(Comment, BaseModel)
        assert issubclass(CommentRef, BaseModel)
        assert issubclass(FailureDetail, BaseModel)
        assert issubclass(BatchResult, BaseModel)

    def test_docs_models_importable_from_submodule(self) -> None:
        from raise_cli.adapters.models.docs import (
            PageContent,
            PageSummary,
            PublishResult,
            SpaceInfo,
        )

        assert issubclass(PageContent, BaseModel)
        assert issubclass(PageSummary, BaseModel)
        assert issubclass(PublishResult, BaseModel)
        assert issubclass(SpaceInfo, BaseModel)

    def test_governance_models_importable_from_submodule(self) -> None:
        from raise_cli.adapters.models.governance import (
            ArtifactLocator,
            CoreArtifactType,
        )

        assert issubclass(ArtifactLocator, BaseModel)
        assert isinstance(CoreArtifactType.ADR, str)

    def test_health_models_importable_from_submodule(self) -> None:
        from raise_cli.adapters.models.health import AdapterHealth

        assert issubclass(AdapterHealth, BaseModel)


class TestBackwardsCompatibility:
    """All existing imports from raise_cli.adapters.models still work."""

    def test_all_public_models_importable_from_package(self) -> None:
        from raise_cli.adapters.models import (
            AdapterHealth,
            ArtifactLocator,
            BatchResult,
            Comment,
            CommentRef,
            CoreArtifactType,
            FailureDetail,
            IssueDetail,
            IssueRef,
            IssueSpec,
            IssueSummary,
            PageContent,
            PageSummary,
            PublishResult,
        )

        # Verify identity — same class, not a copy
        from raise_cli.adapters.models.pm import IssueSpec as IssueSpecDirect

        assert IssueSpec is IssueSpecDirect

    def test_space_info_importable_from_package(self) -> None:
        from raise_cli.adapters.models import SpaceInfo

        assert issubclass(SpaceInfo, BaseModel)


class TestFilesystemModelsExtracted:
    """Filesystem internals live outside the shared models package."""

    def test_backlog_models_importable_from_filesystem_models(self) -> None:
        from raise_cli.adapters.filesystem_models import (
            BacklogComment,
            BacklogItem,
            BacklogLink,
        )

        assert issubclass(BacklogItem, BaseModel)
        assert issubclass(BacklogLink, BaseModel)
        assert issubclass(BacklogComment, BaseModel)

    def test_backlog_models_not_in_models_all(self) -> None:
        import raise_cli.adapters.models as models_pkg

        all_names = getattr(models_pkg, "__all__", [])
        assert "BacklogItem" not in all_names
        assert "BacklogLink" not in all_names
        assert "BacklogComment" not in all_names


class TestSpaceInfo:
    """SpaceInfo model for Confluence discovery (RAISE-1051)."""

    def test_minimal_construction(self) -> None:
        from raise_cli.adapters.models.docs import SpaceInfo

        space = SpaceInfo(key="RaiSE1", name="RaiSE")
        assert space.key == "RaiSE1"
        assert space.name == "RaiSE"
        assert space.url == ""
        assert space.type == "global"

    def test_full_construction(self) -> None:
        from raise_cli.adapters.models.docs import SpaceInfo

        space = SpaceInfo(
            key="RaiSE1",
            name="RaiSE Engineering",
            url="https://humansys.atlassian.net/wiki/spaces/RaiSE1",
            type="global",
        )
        assert space.url.endswith("RaiSE1")

    def test_roundtrip(self) -> None:
        from raise_cli.adapters.models.docs import SpaceInfo

        space = SpaceInfo(key="DEV", name="Development")
        rebuilt = SpaceInfo.model_validate(space.model_dump())
        assert rebuilt == space

    def test_is_basemodel(self) -> None:
        from raise_cli.adapters.models.docs import SpaceInfo

        assert issubclass(SpaceInfo, BaseModel)
