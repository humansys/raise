"""Tests for version parsing, validation, and bumping."""

from __future__ import annotations

import pytest

from raise_cli.publish.version import (
    bump_version,
    is_pep440,
    parse_version,
    sync_version_files,
)


class TestIsPep440:
    """Test PEP 440 validation."""

    @pytest.mark.parametrize(
        "version",
        [
            "2.0.0",
            "2.0.0a7",
            "2.0.0b1",
            "2.0.0rc1",
            "1.0.0",
            "0.1.0",
            "3.2.1a1",
        ],
    )
    def test_valid_versions(self, version: str) -> None:
        assert is_pep440(version) is True

    @pytest.mark.parametrize(
        "version",
        [
            "2.0.0-alpha.7",
            "2.0.0-beta.1",
            "v2.0.0",
            "not-a-version",
            "",
            "2.0",
        ],
    )
    def test_invalid_versions(self, version: str) -> None:
        assert is_pep440(version) is False


class TestParseVersion:
    """Test version parsing."""

    def test_parse_stable(self) -> None:
        v = parse_version("2.0.0")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 0
        assert v.pre_type is None
        assert v.pre_num is None

    def test_parse_alpha(self) -> None:
        v = parse_version("2.0.0a7")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 0
        assert v.pre_type == "a"
        assert v.pre_num == 7

    def test_parse_beta(self) -> None:
        v = parse_version("2.0.0b3")
        assert v.pre_type == "b"
        assert v.pre_num == 3

    def test_parse_rc(self) -> None:
        v = parse_version("1.2.3rc2")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.pre_type == "rc"
        assert v.pre_num == 2

    def test_parse_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="not a valid PEP 440"):
            parse_version("2.0.0-alpha.7")

    def test_str_roundtrip_stable(self) -> None:
        assert str(parse_version("2.0.0")) == "2.0.0"

    def test_str_roundtrip_pre(self) -> None:
        assert str(parse_version("2.0.0a7")) == "2.0.0a7"
        assert str(parse_version("1.0.0rc1")) == "1.0.0rc1"


class TestBumpVersion:
    """Test version bumping."""

    def test_bump_alpha(self) -> None:
        assert bump_version("2.0.0a7", "alpha") == "2.0.0a8"

    def test_bump_beta_from_alpha(self) -> None:
        assert bump_version("2.0.0a7", "beta") == "2.0.0b1"

    def test_bump_beta_from_beta(self) -> None:
        assert bump_version("2.0.0b1", "beta") == "2.0.0b2"

    def test_bump_rc_from_beta(self) -> None:
        assert bump_version("2.0.0b3", "rc") == "2.0.0rc1"

    def test_bump_rc_from_rc(self) -> None:
        assert bump_version("2.0.0rc1", "rc") == "2.0.0rc2"

    def test_bump_release_from_pre(self) -> None:
        assert bump_version("2.0.0a7", "release") == "2.0.0"
        assert bump_version("2.0.0rc2", "release") == "2.0.0"

    def test_bump_patch(self) -> None:
        assert bump_version("2.0.0", "patch") == "2.0.1"

    def test_bump_minor(self) -> None:
        assert bump_version("2.0.0", "minor") == "2.1.0"

    def test_bump_major(self) -> None:
        assert bump_version("2.0.0", "major") == "3.0.0"

    def test_bump_alpha_from_stable(self) -> None:
        """Bumping alpha from stable goes to next patch alpha."""
        assert bump_version("2.0.0", "alpha") == "2.0.1a1"

    def test_bump_patch_resets_minor(self) -> None:
        assert bump_version("2.3.5", "minor") == "2.4.0"

    def test_bump_major_resets_all(self) -> None:
        assert bump_version("2.3.5", "major") == "3.0.0"


class TestSyncVersionFiles:
    """Test version file synchronization."""

    def test_sync_pyproject(self, tmp_path: pytest.TempPathFactory) -> None:
        pyproject = tmp_path / "pyproject.toml"  # type: ignore[operator]
        pyproject.write_text('version = "2.0.0a7"\n')

        init_py = tmp_path / "__init__.py"  # type: ignore[operator]
        init_py.write_text('__version__ = "2.0.0a7"\n')

        sync_version_files(
            "2.1.0",
            pyproject_path=pyproject,  # type: ignore[arg-type]
            init_path=init_py,  # type: ignore[arg-type]
        )

        assert 'version = "2.1.0"' in pyproject.read_text(encoding="utf-8")
        assert '__version__ = "2.1.0"' in init_py.read_text(encoding="utf-8")

    def test_sync_preserves_surrounding_content(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        pyproject = tmp_path / "pyproject.toml"  # type: ignore[operator]
        pyproject.write_text(
            '[project]\nname = "test"\nversion = "1.0.0"\ndescription = "hi"\n'
        )

        init_py = tmp_path / "__init__.py"  # type: ignore[operator]
        init_py.write_text('"""Module."""\n__version__ = "1.0.0"\n__author__ = "me"\n')

        sync_version_files(
            "1.1.0",
            pyproject_path=pyproject,  # type: ignore[arg-type]
            init_path=init_py,  # type: ignore[arg-type]
        )

        pyproject_content = pyproject.read_text(encoding="utf-8")
        assert 'name = "test"' in pyproject_content
        assert 'version = "1.1.0"' in pyproject_content
        assert 'description = "hi"' in pyproject_content

        init_content = init_py.read_text(encoding="utf-8")
        assert '__version__ = "1.1.0"' in init_content
        assert '__author__ = "me"' in init_content
