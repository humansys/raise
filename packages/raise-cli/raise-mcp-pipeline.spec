# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir spec for the `rai-mcp-pipeline` binary (RAISE-15629).

Run from packages/raise-cli/: `pyinstaller raise-mcp-pipeline.spec`.

Same critical flags as raise-cli.spec (see that file's docstring for the
spike evidence) — `rai-mcp-pipeline` is the primary agentic surface
(~36 MCP tools over stdio) and shares raise_cli/raise_core as its
dependency closure, so it needs the same copy_metadata/collect_submodules
treatment.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

MCP_PIPELINE_MAIN = "src/raise_cli/pipeline/mcp_server.py"

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
    [MCP_PIPELINE_MAIN],
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
    name="rai-mcp-pipeline",
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="rai-mcp-pipeline",
)
