"""Tests for TypeScriptAnalyzer."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from raise_cli.context.analyzers.protocol import CodeAnalyzer
from raise_cli.context.analyzers.typescript import TypeScriptAnalyzer


class TestTypeScriptAnalyzerDetect:
    """Tests for TypeScriptAnalyzer.detect()."""

    def test_detects_ts_project_with_tsconfig(self, tmp_path: Path) -> None:
        """Should detect TypeScript when tsconfig.json exists."""
        (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')
        analyzer = TypeScriptAnalyzer(src_dir="src")
        assert analyzer.detect(tmp_path) is True

    def test_detects_ts_project_with_package_json_and_ts_files(
        self, tmp_path: Path
    ) -> None:
        """Should detect TypeScript when package.json exists and .ts files are present."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        src = tmp_path / "src"
        src.mkdir()
        (src / "index.ts").write_text("export const x = 1;\n")
        analyzer = TypeScriptAnalyzer(src_dir="src")
        assert analyzer.detect(tmp_path) is True

    def test_does_not_detect_without_ts_markers(self, tmp_path: Path) -> None:
        """Should not detect TypeScript without tsconfig.json or package.json."""
        analyzer = TypeScriptAnalyzer(src_dir="src")
        assert analyzer.detect(tmp_path) is False

    def test_does_not_detect_package_json_without_ts_files(
        self, tmp_path: Path
    ) -> None:
        """package.json alone (no .ts files) should not trigger detection."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        src = tmp_path / "src"
        src.mkdir()
        (src / "index.js").write_text("module.exports = {};\n")
        analyzer = TypeScriptAnalyzer(src_dir="src")
        assert analyzer.detect(tmp_path) is False

    def test_implements_code_analyzer_protocol(self) -> None:
        """TypeScriptAnalyzer should satisfy CodeAnalyzer Protocol."""
        analyzer = TypeScriptAnalyzer(src_dir="src")
        assert isinstance(analyzer, CodeAnalyzer)


class TestTypeScriptAnalyzerImports:
    """Tests for import extraction."""

    def _make_ts_project(
        self,
        tmp_path: Path,
        module_name: str,
        filename: str,
        code: str,
    ) -> Path:
        """Helper to create a TS module with given code."""
        src_dir = tmp_path / "src"
        mod_dir = src_dir / module_name
        mod_dir.mkdir(parents=True)
        (mod_dir / filename).write_text(dedent(code))
        (tmp_path / "tsconfig.json").write_text("{}")
        return src_dir

    def test_extracts_named_import_relative(self, tmp_path: Path) -> None:
        """Should extract module name from relative named import."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "run.ts").write_text("import { Runner } from '../core/runner';\n")
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text("export class Runner {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert "core" in cmd_info.imports

    def test_extracts_default_import_relative(self, tmp_path: Path) -> None:
        """Should extract module name from relative default import."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "index.ts").write_text("import Runner from '../core/runner';\n")
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text("export default class Runner {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert "core" in cmd_info.imports

    def test_extracts_namespace_import(self, tmp_path: Path) -> None:
        """Should extract module name from namespace import (import * as ...)."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "index.ts").write_text(
            "import * as utils from '../utils/helpers';\n"
        )
        utils = src / "utils"
        utils.mkdir(parents=True)
        (utils / "helpers.ts").write_text("export function help() {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert "utils" in cmd_info.imports

    def test_extracts_type_only_import(self, tmp_path: Path) -> None:
        """Should extract module name from type-only imports."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "index.ts").write_text(
            "import type { Config } from '../config/types';\n"
        )
        config = src / "config"
        config.mkdir(parents=True)
        (config / "types.ts").write_text("export interface Config {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert "config" in cmd_info.imports

    def test_ignores_external_package_imports(self, tmp_path: Path) -> None:
        """Should not include external package imports (no ./ or ../)."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "index.ts").write_text(
            dedent("""\
            import express from 'express';
            import { z } from 'zod';
            import * as path from 'path';
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert cmd_info.imports == []

    def test_ignores_self_imports(self, tmp_path: Path) -> None:
        """Should not include imports from the same module."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "run.ts").write_text("import { helper } from './utils';\n")
        (commands / "utils.ts").write_text("export function helper() {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert "commands" not in cmd_info.imports

    def test_deduplicates_imports(self, tmp_path: Path) -> None:
        """Should not list the same imported module twice."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "a.ts").write_text("import { Foo } from '../core/foo';\n")
        (commands / "b.ts").write_text("import { Bar } from '../core/bar';\n")
        core = src / "core"
        core.mkdir(parents=True)
        (core / "foo.ts").write_text("export class Foo {}\n")
        (core / "bar.ts").write_text("export class Bar {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert cmd_info.imports == ["core"]

    def test_skips_d_ts_files(self, tmp_path: Path) -> None:
        """Should skip .d.ts declaration files."""
        src = tmp_path / "src"
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "types.d.ts").write_text(
            "import { SomeType } from '../core/types';\n"
        )
        (commands / "index.ts").write_text("export function run() {}\n")
        core = src / "core"
        core.mkdir(parents=True)
        (core / "types.ts").write_text("export interface SomeType {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        cmd_info = next((m for m in modules if m.name == "commands"), None)
        assert cmd_info is not None
        assert cmd_info.imports == []

    def test_handles_tsx_files(self, tmp_path: Path) -> None:
        """Should parse .tsx files and extract imports."""
        src = tmp_path / "src"
        components = src / "components"
        components.mkdir(parents=True)
        (components / "App.tsx").write_text(
            "import { Runner } from '../core/runner';\nexport function App() {}\n"
        )
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text("export class Runner {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        comp_info = next((m for m in modules if m.name == "components"), None)
        assert comp_info is not None
        assert "core" in comp_info.imports
        assert "App" in comp_info.exports

    def test_handles_unreadable_file(self, tmp_path: Path) -> None:
        """Should skip unreadable files gracefully."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        f = core / "broken.ts"
        f.write_text("export class Good {}\n")
        f.chmod(0o000)
        (core / "ok.ts").write_text("export class Ok {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "Ok" in core_info.exports
        # Restore permissions for cleanup
        f.chmod(0o644)


class TestTypeScriptAnalyzerExports:
    """Tests for export extraction from barrel files (index.ts)."""

    def test_extracts_named_exports(self, tmp_path: Path) -> None:
        """Should extract named exports."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text(
            dedent("""\
            export class Runner {}
            export function run() {}
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "Runner" in core_info.exports
        assert "run" in core_info.exports

    def test_extracts_default_export(self, tmp_path: Path) -> None:
        """Should extract default exports (as 'default')."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text("export default class Runner {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "Runner" in core_info.exports

    def test_extracts_reexports_from_barrel(self, tmp_path: Path) -> None:
        """Should extract re-exports from barrel file (index.ts)."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text(
            dedent("""\
            export { Runner } from './runner';
            export { Config } from './config';
            """)
        )
        (core / "runner.ts").write_text("export class Runner {}\n")
        (core / "config.ts").write_text("export interface Config {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "Runner" in core_info.exports
        assert "Config" in core_info.exports

    def test_extracts_aliased_export(self, tmp_path: Path) -> None:
        """Should use alias name for export { Foo as Bar }."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text(
            "export { InternalRunner as Runner } from './runner';\n"
        )
        (core / "runner.ts").write_text("export class InternalRunner {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "Runner" in core_info.exports
        # The alias is exported, not the internal name (from index.ts)
        # But InternalRunner also appears from runner.ts direct export
        assert "InternalRunner" in core_info.exports

    def test_extracts_default_export_function(self, tmp_path: Path) -> None:
        """Should extract name from export default function."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "helper.ts").write_text("export default function createApp() {}\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "createApp" in core_info.exports

    def test_extracts_exported_const(self, tmp_path: Path) -> None:
        """Should extract exported const/let/var declarations."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "constants.ts").write_text(
            dedent("""\
            export const VERSION = '1.0';
            export let counter = 0;
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert "VERSION" in core_info.exports
        assert "counter" in core_info.exports


class TestTypeScriptAnalyzerComponents:
    """Tests for component counting."""

    def test_counts_classes_and_functions(self, tmp_path: Path) -> None:
        """Should count classes and functions."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "models.ts").write_text(
            dedent("""\
            class Foo {}
            class Bar {}
            function helper() {}
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert core_info.component_count == 3

    def test_counts_interfaces_and_enums(self, tmp_path: Path) -> None:
        """Should count interfaces and enums."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "types.ts").write_text(
            dedent("""\
            interface Config {}
            enum Status { Active, Inactive }
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert core_info.component_count == 2

    def test_counts_type_aliases(self, tmp_path: Path) -> None:
        """Should count type aliases."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "types.ts").write_text(
            dedent("""\
            type ID = string;
            type Result<T> = { data: T; error?: string };
            """)
        )
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        core_info = next((m for m in modules if m.name == "core"), None)
        assert core_info is not None
        assert core_info.component_count == 2


class TestTypeScriptAnalyzerModuleDiscovery:
    """Tests for full module analysis."""

    def test_discovers_top_level_directories_as_modules(self, tmp_path: Path) -> None:
        """Top-level subdirectories under src/ are modules."""
        src = tmp_path / "src"
        for name in ["commands", "core", "utils"]:
            mod = src / name
            mod.mkdir(parents=True)
            (mod / "index.ts").write_text("export {};\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        names = sorted(m.name for m in modules)
        assert names == ["commands", "core", "utils"]

    def test_skips_node_modules_and_hidden_dirs(self, tmp_path: Path) -> None:
        """Should skip node_modules and hidden directories."""
        src = tmp_path / "src"
        # Valid module
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text("export {};\n")
        # node_modules — skip
        nm = src / "node_modules"
        nm.mkdir(parents=True)
        (nm / "index.ts").write_text("export {};\n")
        # hidden dir — skip
        hidden = src / ".internal"
        hidden.mkdir(parents=True)
        (hidden / "index.ts").write_text("export {};\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        names = [m.name for m in modules]
        assert names == ["core"]

    def test_sets_language_to_typescript(self, tmp_path: Path) -> None:
        """All modules should have language='typescript'."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text("export {};\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules[0].language == "typescript"

    def test_sets_source_path(self, tmp_path: Path) -> None:
        """source_path should be relative path to the module dir."""
        src = tmp_path / "src"
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text("export {};\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules[0].source_path == "src/core"

    def test_handles_no_modules(self, tmp_path: Path) -> None:
        """Should return empty list when src_dir has no subdirs."""
        src = tmp_path / "src"
        src.mkdir(parents=True)
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules == []

    def test_handles_missing_src_dir(self, tmp_path: Path) -> None:
        """Should return empty list when src_dir doesn't exist."""
        (tmp_path / "tsconfig.json").write_text("{}")
        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules == []

    def test_module_requires_ts_files(self, tmp_path: Path) -> None:
        """Directories without .ts/.tsx files should be skipped."""
        src = tmp_path / "src"
        # Dir with only non-TS files
        data = src / "data"
        data.mkdir(parents=True)
        (data / "readme.txt").write_text("not a module")
        # Dir with TS files
        core = src / "core"
        core.mkdir(parents=True)
        (core / "index.ts").write_text("export {};\n")
        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        names = [m.name for m in modules]
        assert names == ["core"]

    def test_full_analysis_with_imports_exports_components(
        self, tmp_path: Path
    ) -> None:
        """Integration: full analysis with imports, exports, and components."""
        src = tmp_path / "src"

        # core module — exports Runner, has no imports
        core = src / "core"
        core.mkdir(parents=True)
        (core / "runner.ts").write_text(
            dedent("""\
            export class Runner {
                run(): void {}
            }
            export function createRunner(): Runner {
                return new Runner();
            }
            """)
        )
        (core / "index.ts").write_text(
            "export { Runner, createRunner } from './runner';\n"
        )

        # commands module — imports core
        commands = src / "commands"
        commands.mkdir(parents=True)
        (commands / "run.ts").write_text(
            dedent("""\
            import { Runner } from '../core/runner';

            export function runCommand(): void {
                const r = new Runner();
                r.run();
            }
            """)
        )

        (tmp_path / "tsconfig.json").write_text("{}")

        analyzer = TypeScriptAnalyzer(src_dir="src")
        modules = analyzer.analyze_modules(tmp_path)

        assert len(modules) == 2

        core_info = next(m for m in modules if m.name == "core")
        assert core_info.language == "typescript"
        assert "Runner" in core_info.exports
        assert "createRunner" in core_info.exports
        assert core_info.component_count >= 2  # Runner class + createRunner function
        assert core_info.imports == []  # no cross-module imports

        cmd_info = next(m for m in modules if m.name == "commands")
        assert "core" in cmd_info.imports
        assert "runCommand" in cmd_info.exports
        assert cmd_info.component_count >= 1  # runCommand function
