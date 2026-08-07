"""Public distribution smoke tests that do not depend on private repo scaffolding."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

import raise_cli
from raise_cli.cli.main import app
from raise_cli.skills_base import DISTRIBUTABLE_SKILLS


def test_public_package_metadata_is_consistent() -> None:
    """The import surface must report the package's public license."""
    assert raise_cli.__version__.startswith("3.1.0")
    assert raise_cli.__license__ == "Apache-2.0"


def test_public_cli_help_is_available() -> None:
    """The installed console application must start without repo-local files."""
    result = CliRunner().invoke(app, ["--help"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "RaiSE" in result.output


def test_public_codex_init_scaffolds_plugin_surface(tmp_path: Path) -> None:
    """A customer install must provision Codex skills and plugin manifests."""
    project = tmp_path / "customer-project"
    rai_home = tmp_path / "rai-home"
    project.mkdir()
    rai_home.mkdir()

    with patch("raise_cli.onboarding.profile.get_rai_home", return_value=rai_home):
        result = CliRunner().invoke(
            app,
            ["init", "--path", str(project), "--agent", "codex"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    installed_skills = {
        path.parent.name
        for path in (project / ".agent" / "skills").glob("rai-*/SKILL.md")
    }
    assert installed_skills == set(DISTRIBUTABLE_SKILLS)
    assert len(installed_skills) >= 70
    assert (project / ".codex" / "hooks.json").is_file()
    assert (project / ".codex" / "config.toml").is_file()
    assert (
        project / "plugins" / "raise-governance" / ".codex-plugin" / "plugin.json"
    ).is_file()
    assert (project / ".agents" / "plugins" / "marketplace.json").is_file()
