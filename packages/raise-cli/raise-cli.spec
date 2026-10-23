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

tree_sitter_c_sharp (RAISE-17096): now a default raise-cli dependency
(previously only reachable transitively via tree-sitter-language-pack) —
collected explicitly for the same static-analysis reason as above, so C#
discovery works in the packaged binary without the `[csharp]` extra.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

CLI_MAIN = "src/raise_cli/cli/main.py"

# RAISE-15800: ONNX model for OnnxEmbeddingProvider (sys.frozen path).
# CI exports intfloat/multilingual-e5-base to int8 ONNX before invoking pyinstaller.
# The directory is optional — build proceeds without it for non-embedding binaries.
_MODEL_DIR = Path(SPECPATH) / "models" / "multilingual-e5-base"
_model_datas = [(str(_MODEL_DIR), "models/multilingual-e5-base")] if _MODEL_DIR.exists() else []

datas = (
    copy_metadata("raise-cli")
    + copy_metadata("raise-core")
    + collect_data_files("raise_cli")
    + _model_datas
)
hiddenimports = (
    collect_submodules("raise_cli")
    + collect_submodules("raise_core")
    + collect_submodules("tree_sitter_language_pack")
    + collect_submodules("tree_sitter_c_sharp")
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
