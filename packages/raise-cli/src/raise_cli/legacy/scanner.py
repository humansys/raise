"""Legacy residue scanner -- pure detection, no writes, no recursive walks.

All detection functions are stat/glob only.  Never execute a foreign python,
never walk the full project tree recursively.

``scan_project(root)`` composes the per-project families; ``scan_global()``
covers installations outside the project.  Both return ``ScanReport`` /
``list[Residue]`` respectively.

Architecture: Epic RAISE-16227 design S1, I2.
"""

from __future__ import annotations

import glob as glob_mod
import json
import logging
import re
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.legacy.models import Residue, ScanReport

logger = logging.getLogger(__name__)

# Known venv directory names at project root / worktree root.
_KNOWN_VENV_NAMES: frozenset[str] = frozenset({".venv", "venv", ".venv-mcp"})

# Pre-rename package names (advisory kind: venv-prerename-pkg).
_PRERENAME_DIST_PACKAGES: frozenset[str] = frozenset({"rai_cli", "rai_core"})

# Console script names that indicate a legacy entry point.
_CONSOLE_SCRIPT_NAMES: tuple[str, ...] = ("rai", "rai-mcp-pipeline")

# Runtime config relative paths (same as worktree/provision.py).
_RUNTIME_CONFIG_RELS: tuple[str, ...] = (".codex/config.toml", ".hermes/config.yaml")

# Files whose presence in instances/ means superseded layout.
_LOOSE_EMBEDDING_FILES: frozenset[str] = frozenset({
    "embeddings.npy",
    "embedding_index.json",
    "fingerprints.json",
})

# Regex matching raise-cli/raise-core/rai-cli/rai-core in dependency contexts.
# Allows start-of-line, whitespace, or quote before the name.
DEP_RE = re.compile(
    r"""(?:^|[\s"'])(raise-cli|raise-core|rai-cli|rai-core)(?:[\[><=!~\s"']|$)""",
    re.IGNORECASE,
)

# Regex for extracting command paths from runtime configs (TOML/YAML).
_CMD_RE = re.compile(r"""(?:path|command)\s*[=:]\s*["']?([^\s"']+)""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_absolute_path(path: str) -> bool:
    """Check if a string looks like an absolute path (POSIX or Windows)."""
    return path.startswith("/") or (len(path) > 2 and path[1] == ":")


def _site_packages_dirs(venv_dir: Path) -> list[Path]:
    """Locate site-packages inside a venv (POSIX and Windows layouts)."""
    candidates: list[Path] = []
    # POSIX: lib/python*/site-packages
    posix_pattern = str(venv_dir / "lib" / "python*" / "site-packages")
    candidates.extend(Path(p) for p in glob_mod.glob(posix_pattern))
    # Windows: Lib/site-packages
    win_sp = venv_dir / "Lib" / "site-packages"
    if win_sp.is_dir():
        candidates.append(win_sp)
    return candidates


def _bin_dir(venv_dir: Path) -> Path | None:
    """Locate the scripts directory inside a venv."""
    for name in ("bin", "Scripts"):
        d = venv_dir / name
        if d.is_dir():
            return d
    return None


def _detect_version_from_dist_info(sp_dir: Path, pkg_underscore: str) -> str:
    """Extract version from a dist-info METADATA file, best-effort."""
    pattern = str(sp_dir / f"{pkg_underscore}-*.dist-info" / "METADATA")
    for metadata_path in glob_mod.glob(pattern):
        try:
            for line in Path(metadata_path).read_text().splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            continue
    return "unknown"


def _venv_roots(root: Path) -> list[Path]:
    """Enumerate venv candidate directories at project root + worktrees."""
    candidates: list[Path] = []
    for name in _KNOWN_VENV_NAMES:
        d = root / name
        if d.is_dir():
            candidates.append(d)
    worktrees_dir = root / ".worktree"
    if worktrees_dir.is_dir():
        try:
            for wt_dir in sorted(worktrees_dir.iterdir()):
                if wt_dir.is_dir():
                    for name in _KNOWN_VENV_NAMES:
                        d = wt_dir / name
                        if d.is_dir():
                            candidates.append(d)
        except OSError:
            pass
    return candidates


# ---------------------------------------------------------------------------
# scan_venvs
# ---------------------------------------------------------------------------


def scan_venvs(root: Path) -> list[Residue]:
    """Detect venv residues: raise-cli, pre-rename, console scripts, renamed.

    Scans known venv names at project root and worktree roots, plus
    depth-1 children with ``pyvenv.cfg`` for renamed venvs.
    """
    residues: list[Residue] = []

    for venv_dir in _venv_roots(root):
        _scan_single_venv(venv_dir, residues)

    # Depth-1 scan for renamed venvs (pyvenv.cfg detection)
    try:
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in _KNOWN_VENV_NAMES:
                continue
            if (child / "pyvenv.cfg").is_file():
                residues.append(
                    Residue.create(
                        "venv-renamed",
                        child,
                        evidence={"reason": "pyvenv.cfg present, non-standard name"},
                        action_hint="move outside project tree to prevent indexing",
                    )
                )
    except OSError:
        pass

    return residues


def _scan_single_venv(venv_dir: Path, residues: list[Residue]) -> None:
    """Scan a single venv directory for legacy packages and console scripts."""
    for sp_dir in _site_packages_dirs(venv_dir):
        _scan_venv_packages(sp_dir, venv_dir, residues)
    _scan_venv_scripts(venv_dir, residues)


def _scan_venv_packages(
    sp_dir: Path, venv_dir: Path, residues: list[Residue],
) -> None:
    """Check site-packages for raise-cli and pre-rename dist-info."""
    # Current name: raise-cli
    if glob_mod.glob(str(sp_dir / "raise_cli-*.dist-info")):
        version = _detect_version_from_dist_info(sp_dir, "raise_cli")
        residues.append(
            Residue.create(
                "venv-raise-cli",
                venv_dir,
                evidence={"version": version, "package": "raise-cli"},
                action_hint="pip uninstall raise-cli or remove the venv",
            )
        )

    # Pre-rename packages (rai-cli, rai-core)
    for pkg in _PRERENAME_DIST_PACKAGES:
        if glob_mod.glob(str(sp_dir / f"{pkg}-*.dist-info")):
            version = _detect_version_from_dist_info(sp_dir, pkg)
            residues.append(
                Residue.create(
                    "venv-prerename-pkg",
                    venv_dir,
                    evidence={"version": version, "package": pkg.replace("_", "-")},
                    action_hint=f"pip uninstall {pkg.replace('_', '-')}",
                )
            )


def _scan_venv_scripts(venv_dir: Path, residues: list[Residue]) -> None:
    """Check bin/Scripts for rai console scripts."""
    bd = _bin_dir(venv_dir)
    if bd is None:
        return
    for script_name in _CONSOLE_SCRIPT_NAMES:
        for ext in ("", ".exe"):
            script = bd / f"{script_name}{ext}"
            if script.is_file():
                residues.append(
                    Residue.create(
                        "venv-console-script",
                        script,
                        evidence={"script": script_name},
                        action_hint="may resolve before the global binary",
                    )
                )
                break  # don't report both plain and .exe


# ---------------------------------------------------------------------------
# scan_dep_declarations
# ---------------------------------------------------------------------------


def scan_dep_declarations(root: Path) -> list[Residue]:
    """Detect dependency declarations referencing raise-cli / rai-cli / rai-core.

    Checks: ``requirements*.txt``, ``pyproject.toml`` dependencies, ``uv.lock``.
    """
    residues: list[Residue] = []
    _scan_requirements_files(root, residues)
    _scan_pyproject_deps(root, residues)
    _scan_uvlock(root, residues)
    return residues


def _scan_requirements_files(root: Path, residues: list[Residue]) -> None:
    """Check requirements*.txt for raise-cli lines."""
    for req_path in sorted(Path(p) for p in glob_mod.glob(str(root / "requirements*.txt"))):
        try:
            for line in req_path.read_text().splitlines():
                if DEP_RE.search(line):
                    residues.append(
                        Residue.create(
                            "requirements-dep",
                            req_path,
                            evidence={"line": line.strip()},
                            action_hint="remove the raise-cli/raise-core line",
                        )
                    )
                    break  # one residue per file
        except OSError:
            continue


def _scan_pyproject_deps(root: Path, residues: list[Residue]) -> None:
    """Check pyproject.toml for raise-cli in dependencies."""
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return
    try:
        content = pyproject.read_text()
        if DEP_RE.search(content):
            residues.append(
                Residue.create(
                    "pyproject-dep",
                    pyproject,
                    evidence={"file": "pyproject.toml"},
                    action_hint="remove raise-cli/raise-core from [project.dependencies]",
                )
            )
    except OSError:
        pass


def _scan_uvlock(root: Path, residues: list[Residue]) -> None:
    """Check uv.lock for raise-cli entry."""
    uvlock = root / "uv.lock"
    if not uvlock.is_file():
        return
    try:
        content = uvlock.read_text()
        if re.search(r'name\s*=\s*"(raise-cli|raise-core|rai-cli|rai-core)"', content):
            residues.append(
                Residue.create(
                    "uvlock-entry",
                    uvlock,
                    evidence={"file": "uv.lock"},
                    action_hint="run uv lock after cleanup",
                )
            )
    except OSError:
        pass


# ---------------------------------------------------------------------------
# scan_mcp_configs
# ---------------------------------------------------------------------------


def scan_mcp_configs(root: Path) -> list[Residue]:
    """Detect stale MCP and runtime configs with broken commands.

    - ``stale-mcp-command``: rai-workspace with a missing absolute command
      path.  Bare commands (no path separator) are intentionally not
      checked (F4/S2-D2: ``shutil.which`` depends on the invoking
      shell's PATH, not the MCP client's runtime env).
    - ``stale-runtime-config``: codex/hermes config with absolute venv command missing.
    - ``user-mcp-dangling``: non-rai entries with absolute missing command.
    """
    residues: list[Residue] = []
    _scan_mcp_json(root, residues)
    _scan_runtime_configs(root, residues)
    return residues


def _scan_mcp_json(root: Path, residues: list[Residue]) -> None:
    """Parse .mcp.json and check server commands.

    F3: isinstance guards at each level -- non-dict top level, non-dict
    mcpServers, non-dict server entry, non-str command all skip silently.
    """
    mcp_path = root / ".mcp.json"
    if not mcp_path.is_file():
        return
    try:
        data: object = json.loads(mcp_path.read_text())
    except (json.JSONDecodeError, OSError):
        return

    if not isinstance(data, dict):
        return
    servers_raw: object = data.get("mcpServers", {})
    if not isinstance(servers_raw, dict):
        return

    for server_name, server_cfg in servers_raw.items():
        if not isinstance(server_cfg, dict):
            continue
        command = server_cfg.get("command", "")
        if not isinstance(command, str) or not command:
            continue
        if server_name == "rai-workspace":
            _check_rai_workspace_command(mcp_path, command, server_name, residues)
        elif _is_absolute_path(command) and not Path(command).is_file():
            residues.append(
                Residue.create(
                    "user-mcp-dangling",
                    mcp_path,
                    evidence={"server": server_name, "command": command},
                    action_hint=f"fix or remove the {server_name} entry",
                )
            )


def _check_rai_workspace_command(
    mcp_path: Path, command: str, server_name: str, residues: list[Residue],
) -> None:
    """Check the rai-workspace command for staleness.

    F4: only absolute-missing is flagged.  Bare commands (e.g.
    ``"rai-mcp-pipeline"`` without a path) are NEVER residues --
    ``shutil.which`` depends on the invoking shell's PATH, not the MCP
    client's runtime env, so a tracked ``.mcp.json`` with a bare command
    in dev repos would false-positive.
    """
    if _is_absolute_path(command) and not Path(command).is_file():
        residues.append(
            Residue.create(
                "stale-mcp-command",
                mcp_path,
                evidence={"server": server_name, "command": command},
                action_hint="run: rai clean --fix-config",
            )
        )
    # Bare commands are intentionally not checked (F4/S2-D2).


def _scan_runtime_configs(root: Path, residues: list[Residue]) -> None:
    """Check .codex/config.toml and .hermes/config.yaml for stale commands."""
    for config_rel in _RUNTIME_CONFIG_RELS:
        config_path = root / config_rel
        if not config_path.is_file():
            continue
        try:
            content = config_path.read_text()
        except OSError:
            continue
        for match in _CMD_RE.finditer(content):
            cmd = match.group(1)
            if _is_absolute_path(cmd) and ".venv" in cmd and not Path(cmd).is_file():
                residues.append(
                    Residue.create(
                        "stale-runtime-config",
                        config_path,
                        evidence={"command": cmd},
                        action_hint="run: rai clean --fix-config",
                    )
                )
                break  # one residue per config file


# ---------------------------------------------------------------------------
# scan_cartridge_instances
# ---------------------------------------------------------------------------


def scan_cartridge_instances(root: Path) -> list[Residue]:
    """Detect stale cartridge generations, superseded loose files, repo self-ingest.

    Rules (hallazgo #5):
    - WITH manifest.json: stale = gen-* != generation_dir + loose embedding files.
    - WITHOUT manifest.json: NOTHING is stale (loose files are live data).
    """
    residues: list[Residue] = []
    cartridges_dir = root / ".raise" / "cartridges"
    if not cartridges_dir.is_dir():
        return residues

    try:
        for cart_dir in sorted(cartridges_dir.iterdir()):
            _scan_single_cartridge(cart_dir, residues)
    except OSError:
        pass

    # Repo self-ingest risk — only when CARTRIDGE.yaml lacks snapshot: true
    # (pre RAISE-13378/RAISE-16226 builds). Current builds always write
    # snapshot: true, so the builder skips re-ingesting the repo cartridge.
    repo_cart = root / ".raise" / "cartridges" / "repo"
    repo_json = repo_cart / "instances" / "repo.json"
    if repo_json.is_file():
        manifest_path = repo_cart / "CARTRIDGE.yaml"
        has_snapshot_flag = False
        try:
            content = manifest_path.read_text()
            has_snapshot_flag = "snapshot: true" in content or "snapshot: True" in content
        except OSError:
            pass
        if not has_snapshot_flag:
            residues.append(
                Residue.create(
                    "repo-cartridge-self-ingest",
                    repo_json,
                    action_hint="run rai graph build to regenerate with snapshot flag",
                )
            )

    return residues


def _scan_single_cartridge(cart_dir: Path, residues: list[Residue]) -> None:
    """Scan a single cartridge directory for stale generations and loose files."""
    instances_dir = cart_dir / "instances"
    if not instances_dir.is_dir():
        return

    manifest_path = instances_dir / "manifest.json"
    if not manifest_path.is_file():
        return  # No manifest -> nothing is stale (hallazgo #5)

    try:
        manifest_data = json.loads(manifest_path.read_text())
        live_gen = manifest_data.get("generation_dir", "")
    except (json.JSONDecodeError, OSError):
        return

    _detect_stale_generations(instances_dir, cart_dir.name, live_gen, residues)
    _detect_superseded_loose_files(instances_dir, cart_dir.name, residues)


def _detect_stale_generations(
    instances_dir: Path, cart_name: str, live_gen: str, residues: list[Residue],
) -> None:
    """Find gen-* directories that don't match the manifest's live generation."""
    try:
        for child in sorted(instances_dir.iterdir()):
            if child.is_dir() and child.name.startswith("gen-") and child.name != live_gen:
                residues.append(
                    Residue.create(
                        "stale-cartridge-gen",
                        child,
                        evidence={"cartridge": cart_name, "live_gen": live_gen},
                        action_hint="verify manifest and remove manually",
                    )
                )
    except OSError:
        pass


def _detect_superseded_loose_files(
    instances_dir: Path, cart_name: str, residues: list[Residue],
) -> None:
    """Find superseded loose embedding files when manifest exists."""
    for fname in _LOOSE_EMBEDDING_FILES:
        if (instances_dir / fname).is_file():
            residues.append(
                Residue.create(
                    "superseded-instance-files",
                    instances_dir / fname,
                    evidence={"cartridge": cart_name},
                    action_hint="verify manifest points to valid gen-* before removing",
                )
            )
            break  # one residue per cartridge


# ---------------------------------------------------------------------------
# scan_orphan_dbs
# ---------------------------------------------------------------------------


def scan_orphan_dbs(root: Path) -> list[Residue]:
    """Detect orphan per-project SQLite DBs.

    Delegates to ``discover_sources()`` from the consolidation module.
    Maps SourceDb.kind to ResidueKind:
    - ``"global-partition"`` -> ``"orphan-global-partition"``
    - ``"project-local"`` / ``"worktree"`` -> ``"orphan-project-db"``
    """
    from raise_cli.storage.consolidate import discover_sources

    residues: list[Residue] = []

    try:
        sources = discover_sources(root)
    except Exception:  # noqa: BLE001
        logger.debug("discover_sources failed for %s", root, exc_info=True)
        return residues

    for source in sources:
        if source.kind == "global-partition":
            residues.append(
                Residue.create(
                    "orphan-global-partition",
                    source.path,
                    evidence={"project_id": source.project_id},
                    action_hint="run: rai db consolidate",
                )
            )
        elif source.kind in ("project-local", "worktree"):
            residues.append(
                Residue.create(
                    "orphan-project-db",
                    source.path,
                    evidence={"kind": source.kind, "project_id": source.project_id},
                    action_hint="run: rai db consolidate",
                )
            )

    return residues


# ---------------------------------------------------------------------------
# scan_path_shadowing
# ---------------------------------------------------------------------------


def scan_path_shadowing() -> list[Residue]:
    """Detect PATH shadowing: first ``rai`` in PATH != ``sys.executable``.

    Only runs when ``IS_FROZEN`` is True (late-bound via module attribute).
    """
    from raise_cli import compat as compat_mod

    if not compat_mod.IS_FROZEN:
        return []

    import sys

    rai_in_path = shutil.which("rai")
    if rai_in_path is None:
        return []

    try:
        found_resolved = Path(rai_in_path).resolve()
        exe_resolved = Path(sys.executable).resolve()
    except OSError:
        return []

    if found_resolved != exe_resolved:
        return [
            Residue.create(
                "path-shadowing",
                found_resolved,
                evidence={
                    "found_rai": str(found_resolved),
                    "sys_executable": str(exe_resolved),
                },
                action_hint=f"your shell runs {found_resolved}, not the global binary",
            )
        ]

    return []


# ---------------------------------------------------------------------------
# scan_claude_settings_path
# ---------------------------------------------------------------------------

_VENV_BIN_PATTERNS: frozenset[str] = frozenset(
    f"/{name}/bin" for name in _KNOWN_VENV_NAMES
)


def scan_claude_settings_path() -> list[Residue]:
    """Detect hardcoded venv paths in ~/.claude/settings.json env.PATH.

    Returns at most one Residue of kind ``claude-settings-path`` when
    the settings file contains env.PATH entries matching known venv
    bin directories.  Silently returns [] on missing file, parse
    errors, or absent keys.
    """
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.is_file():
        return []

    try:
        data: object = json.loads(settings_path.read_text())
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, dict):
        return []
    env: object = data.get("env")
    if not isinstance(env, dict):
        return []
    path_val: object = env.get("PATH")
    if not isinstance(path_val, str):
        return []

    offending = [
        entry
        for entry in path_val.split(":")
        if any(pattern in entry for pattern in _VENV_BIN_PATTERNS)
    ]
    if not offending:
        return []

    return [
        Residue.create(
            "claude-settings-path",
            settings_path,
            evidence={"entries": ":".join(offending)},
            action_hint=(
                "remove venv PATH entries from ~/.claude/settings.json env.PATH; "
                "they shadow the project venv's rai binary"
            ),
        )
    ]


# ---------------------------------------------------------------------------
# scan_global
# ---------------------------------------------------------------------------


def scan_global() -> list[Residue]:
    """Detect global legacy installs outside the project.

    Checks (stat-only on known paths under ``$HOME``):
    - ``pipx-raise-cli``: ``~/.local/pipx/venvs/raise-cli/``
    - ``user-site-raise-cli``: ``~/.local/lib/python*/site-packages/raise_cli/``
    - ``global-console-script``: ``~/.local/bin/rai`` or ``rai-mcp-pipeline``
    - ``dangling-rai-symlink``: broken or venv-targeting symlink at ``~/.local/bin/rai``
    """
    residues: list[Residue] = []
    home = Path.home()

    _scan_global_pipx(home, residues)
    _scan_global_user_site(home, residues)
    _scan_global_console_scripts(home, residues)

    return residues


def _scan_global_pipx(home: Path, residues: list[Residue]) -> None:
    """Check for pipx-installed raise-cli."""
    pipx_venv = home / ".local" / "pipx" / "venvs" / "raise-cli"
    if pipx_venv.is_dir():
        residues.append(
            Residue.create(
                "pipx-raise-cli",
                pipx_venv,
                action_hint="pipx uninstall raise-cli",
            )
        )


def _scan_global_user_site(home: Path, residues: list[Residue]) -> None:
    """Check for raise-cli in user site-packages (--user install).

    F2: also checks Windows APPDATA layout when ``$APPDATA`` is set.
    """
    import os

    # POSIX: ~/.local/lib/python*/site-packages/raise_cli/
    user_sp_pattern = str(
        home / ".local" / "lib" / "python*" / "site-packages" / "raise_cli"
    )
    for sp_match in glob_mod.glob(user_sp_pattern):
        if Path(sp_match).is_dir():
            residues.append(
                Residue.create(
                    "user-site-raise-cli",
                    Path(sp_match),
                    action_hint="pip uninstall raise-cli",
                )
            )
            break  # one residue is enough

    # F2 Windows: %APPDATA%\Python\Python3*\site-packages\raise_cli\
    appdata = os.environ.get("APPDATA")
    if appdata:
        win_pattern = str(
            Path(appdata) / "Python" / "Python3*" / "site-packages" / "raise_cli"
        )
        for sp_match in glob_mod.glob(win_pattern):
            if Path(sp_match).is_dir():
                residues.append(
                    Residue.create(
                        "user-site-raise-cli",
                        Path(sp_match),
                        action_hint="pip uninstall raise-cli",
                    )
                )
                break


def _is_python_shebang(path: Path) -> bool:
    """Return True if *path* starts with a ``#!`` line that references python."""
    try:
        with path.open("rb") as f:
            first_line = f.readline(256)
    except OSError:
        return False
    return first_line.startswith(b"#!") and b"python" in first_line


def _scan_global_console_scripts(home: Path, residues: list[Residue]) -> None:
    """Check global paths for rai scripts (including dangling/venv-targeting symlinks).

    F1 exemptions (S2 carry-forward):
    - Frozen live binary: resolved path == sys.executable and IS_FROZEN.
    - Non-shebang native binary: first bytes are not ``#!...python`` --
      presumed the healthy PyInstaller install.

    F2: also checks Windows APPDATA Scripts paths.
    """
    _scan_console_scripts_posix(home, residues)
    _scan_console_scripts_windows(residues)


def _scan_console_scripts_posix(home: Path, residues: list[Residue]) -> None:
    """POSIX: check ~/.local/bin for rai scripts."""
    import sys

    from raise_cli import compat as compat_mod

    local_bin = home / ".local" / "bin"
    for script_name in _CONSOLE_SCRIPT_NAMES:
        script_path = local_bin / script_name
        if not script_path.exists() and not script_path.is_symlink():
            continue

        if script_path.is_symlink() and _check_symlink_residue(script_path, residues):
            continue

        # Regular file or valid symlink to non-venv
        if script_path.is_file():
            # F1(a): skip the live frozen binary (sys.executable match)
            try:
                if compat_mod.IS_FROZEN and script_path.resolve() == Path(sys.executable).resolve():
                    continue
            except OSError:
                pass

            # F1(b): non-shebang native binary is presumed healthy install
            if not _is_python_shebang(script_path):
                continue

            residues.append(
                Residue.create(
                    "global-console-script",
                    script_path,
                    evidence={"script": script_name},
                    action_hint="may resolve before the global binary",
                )
            )


def _scan_console_scripts_windows(residues: list[Residue]) -> None:
    """F2: check Windows APPDATA for console scripts (.exe)."""
    import os

    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    appdata_path = Path(appdata)
    # %APPDATA%\Python\Python3*\Scripts\{rai,rai-mcp-pipeline}.exe
    for script_name in _CONSOLE_SCRIPT_NAMES:
        pattern = str(appdata_path / "Python" / "Python3*" / "Scripts" / f"{script_name}.exe")
        for match in glob_mod.glob(pattern):
            if Path(match).is_file():
                residues.append(
                    Residue.create(
                        "global-console-script",
                        Path(match),
                        evidence={"script": script_name, "source": "windows-appdata"},
                        action_hint="may resolve before the global binary",
                    )
                )
                break  # one per script name


def _check_symlink_residue(script_path: Path, residues: list[Residue]) -> bool:
    """Check if a symlink is dangling or targets a venv.  Returns True if handled."""
    try:
        target = script_path.resolve()
    except OSError:
        return True

    if not target.exists():
        residues.append(
            Residue.create(
                "dangling-rai-symlink",
                script_path,
                evidence={"target": str(target)},
                action_hint="reinstall the global binary",
            )
        )
        return True

    target_str = str(target)
    if ".venv" in target_str or "/venv/" in target_str:
        residues.append(
            Residue.create(
                "dangling-rai-symlink",
                script_path,
                evidence={"target": target_str},
                action_hint="reinstall the global binary",
            )
        )
        return True

    return False


# ---------------------------------------------------------------------------
# scan_project (composition)
# ---------------------------------------------------------------------------


def scan_project(root: Path) -> ScanReport:
    """Compose all per-project scans + path shadowing into a ScanReport.

    Does NOT include ``scan_global()`` -- that is a separate concern
    invoked by ``rai clean`` and ``rai doctor -c legacy``, not by session-open.
    """
    start = time.monotonic()
    residues: list[Residue] = []

    # Per-project families
    for scan_fn in (
        scan_venvs,
        scan_dep_declarations,
        scan_mcp_configs,
        scan_cartridge_instances,
        scan_orphan_dbs,
    ):
        try:
            residues.extend(scan_fn(root))
        except Exception:  # noqa: BLE001
            logger.debug("Scanner %s failed", scan_fn.__name__, exc_info=True)

    # PATH shadowing (cheap, no I/O beyond which())
    try:
        residues.extend(scan_path_shadowing())
    except Exception:  # noqa: BLE001
        logger.debug("scan_path_shadowing failed", exc_info=True)

    # Claude Code settings PATH (cheap, single file read)
    try:
        residues.extend(scan_claude_settings_path())
    except Exception:  # noqa: BLE001
        logger.debug("scan_claude_settings_path failed", exc_info=True)

    elapsed_ms = (time.monotonic() - start) * 1000

    return ScanReport(
        project_root=root,
        residues=residues,
        scanned_at=datetime.now(tz=UTC),
        scan_duration_ms=elapsed_ms,
    )
