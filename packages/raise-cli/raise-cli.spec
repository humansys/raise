# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir spec for the `rai` binary (RAISE-15629).

Run from packages/raise-cli/: `pyinstaller raise-cli.spec`.

Critical flags (measured by the spike, Confluence 3429138455 — without
them entry_points() returns empty and `rai gate list` silently reports 0
gates instead of 41):

- copy_metadata: brings the .dist-info (entry_points.txt) so both
  importlib.metadata.version() and entry_points() resolve in frozen mode.
- collect_submodules: physically bundles the real modules that entry
  points reference (gates, adapters, hooks, doctor checks) so they are
  importable, not just declared.

tree_sitter_language_pack (RAISE-15799): raise-cli already depends on it
directly (see raise-cli's pyproject.toml), so it's always present in the
build venv — but it loads its per-language grammar submodules
dynamically, invisible to PyInstaller's static import analysis. Without
collecting it explicitly here, Dart and other pack-only languages drop
out of `rai graph build` silently, with no error.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

CLI_MAIN = "src/raise_cli/cli/main.py"

datas = (
    copy_metadata("raise-cli")
    + copy_metadata("raise-core")
    + collect_data_files("raise_cli")
)
hiddenimports = (
    collect_submodules("raise_cli")
    + collect_submodules("raise_core")
    + collect_submodules("tree_sitter_language_pack")
)

a = Analysis(
    [CLI_MAIN],
    pathex=[SPECPATH],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="rai",
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="rai",
)
