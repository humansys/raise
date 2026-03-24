"""Tests for code scanner (Python, TypeScript, JavaScript, PHP, Svelte, C#)."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.discovery.scanner import (
    ScanResult,
    Symbol,
    _read_gitignore,
    detect_language,
    extract_csharp_symbols,
    extract_javascript_symbols,
    extract_php_symbols,
    extract_python_symbols,
    extract_svelte_symbols,
    extract_symbols,
    extract_typescript_symbols,
    scan_directory,
)


class TestSymbol:
    """Tests for Symbol model."""

    def test_create_class_symbol(self) -> None:
        """Test creating a class symbol."""
        symbol = Symbol(
            name="UserService",
            kind="class",
            file="src/services/user.py",
            line=15,
            signature="class UserService(BaseService)",
            docstring="Handles user operations.",
        )
        assert symbol.name == "UserService"
        assert symbol.kind == "class"
        assert symbol.line == 15
        assert symbol.parent is None

    def test_create_method_symbol(self) -> None:
        """Test creating a method symbol with parent."""
        symbol = Symbol(
            name="get_user",
            kind="method",
            file="src/services/user.py",
            line=20,
            signature="def get_user(self, user_id: str) -> User",
            parent="UserService",
        )
        assert symbol.name == "get_user"
        assert symbol.kind == "method"
        assert symbol.parent == "UserService"

    def test_create_function_symbol(self) -> None:
        """Test creating a standalone function symbol."""
        symbol = Symbol(
            name="process_data",
            kind="function",
            file="utils.py",
            line=5,
            signature="def process_data(data: list) -> dict",
        )
        assert symbol.kind == "function"
        assert symbol.parent is None

    def test_create_enum_symbol(self) -> None:
        """Test creating an enum symbol."""
        symbol = Symbol(
            name="UserRole",
            kind="enum",
            file="roles.ts",
            line=1,
            signature="enum UserRole",
        )
        assert symbol.kind == "enum"

    def test_create_type_alias_symbol(self) -> None:
        """Test creating a type alias symbol."""
        symbol = Symbol(
            name="UserId",
            kind="type_alias",
            file="types.ts",
            line=1,
            signature="type UserId",
        )
        assert symbol.kind == "type_alias"

    def test_create_constant_symbol(self) -> None:
        """Test creating a constant symbol."""
        symbol = Symbol(
            name="MAX_RETRIES",
            kind="constant",
            file="config.ts",
            line=1,
            signature="const MAX_RETRIES",
        )
        assert symbol.kind == "constant"


class TestScanResult:
    """Tests for ScanResult model."""

    def test_empty_result(self) -> None:
        """Test creating an empty scan result."""
        result = ScanResult()
        assert result.symbols == []
        assert result.files_scanned == 0
        assert result.errors == []

    def test_result_with_data(self) -> None:
        """Test creating a populated scan result."""
        symbol = Symbol(
            name="Foo",
            kind="class",
            file="foo.py",
            line=1,
            signature="class Foo",
        )
        result = ScanResult(
            symbols=[symbol],
            files_scanned=1,
            errors=[],
        )
        assert len(result.symbols) == 1
        assert result.files_scanned == 1


class TestExtractPythonSymbols:
    """Tests for extract_python_symbols function."""

    def test_extract_simple_class(self) -> None:
        """Test extracting a simple class."""
        source = dedent("""\
            class MyClass:
                pass
        """)
        symbols = extract_python_symbols(source, "test.py")
        assert len(symbols) == 1
        assert symbols[0].name == "MyClass"
        assert symbols[0].kind == "class"
        assert symbols[0].line == 1
        assert symbols[0].signature == "class MyClass"

    def test_extract_class_with_bases(self) -> None:
        """Test extracting a class with inheritance."""
        source = dedent("""\
            class UserService(BaseService, Mixin):
                pass
        """)
        symbols = extract_python_symbols(source, "test.py")
        assert symbols[0].signature == "class UserService(BaseService, Mixin)"

    def test_extract_class_with_docstring(self) -> None:
        """Test extracting a class with docstring."""
        source = dedent('''\
            class MyClass:
                """This is the docstring."""
                pass
        ''')
        symbols = extract_python_symbols(source, "test.py")
        assert symbols[0].docstring == "This is the docstring."

    def test_extract_method(self) -> None:
        """Test extracting methods from a class."""
        source = dedent("""\
            class MyClass:
                def my_method(self, arg: str) -> int:
                    pass
        """)
        symbols = extract_python_symbols(source, "test.py")
        assert len(symbols) == 2  # class + method

        method = next(s for s in symbols if s.kind == "method")
        assert method.name == "my_method"
        assert method.parent == "MyClass"
        assert "def my_method(self, arg: str) -> int" in method.signature

    def test_extract_async_method(self) -> None:
        """Test extracting async methods."""
        source = dedent("""\
            class MyClass:
                async def fetch_data(self) -> dict:
                    pass
        """)
        symbols = extract_python_symbols(source, "test.py")
        method = next(s for s in symbols if s.kind == "method")
        assert "async def fetch_data" in method.signature

    def test_extract_standalone_function(self) -> None:
        """Test extracting top-level functions."""
        source = dedent("""\
            def process(data: list[int]) -> int:
                return sum(data)
        """)
        symbols = extract_python_symbols(source, "test.py")
        assert len(symbols) == 1
        assert symbols[0].name == "process"
        assert symbols[0].kind == "function"
        assert symbols[0].parent is None

    def test_extract_module_docstring(self) -> None:
        """Test extracting module-level docstring."""
        source = dedent('''\
            """Module docstring."""

            def foo():
                pass
        ''')
        symbols = extract_python_symbols(source, "mymodule.py")
        module = next((s for s in symbols if s.kind == "module"), None)
        assert module is not None
        assert module.name == "mymodule"
        assert module.docstring == "Module docstring."

    def test_extract_complex_file(self) -> None:
        """Test extracting from a file with multiple definitions."""
        source = dedent('''\
            """Utilities module."""

            class Helper:
                """Helper class."""
                def help(self):
                    pass

            class Processor:
                def process(self, data):
                    pass
                def validate(self, data):
                    pass

            def standalone():
                pass
        ''')
        symbols = extract_python_symbols(source, "utils.py")

        # Should have: 1 module + 2 classes + 3 methods + 1 function = 7
        assert len(symbols) == 7

        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]
        functions = [s for s in symbols if s.kind == "function"]
        modules = [s for s in symbols if s.kind == "module"]

        assert len(classes) == 2
        assert len(methods) == 3
        assert len(functions) == 1
        assert len(modules) == 1

    def test_invalid_syntax_raises(self) -> None:
        """Test that invalid syntax raises SyntaxError."""
        source = "class invalid syntax here"
        with pytest.raises(SyntaxError):
            extract_python_symbols(source, "bad.py")


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_single_file(self, tmp_path: Path) -> None:
        """Test scanning a directory with one file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("class Foo: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1
        assert len(result.symbols) == 1
        assert result.symbols[0].name == "Foo"

    def test_scan_nested_directories(self, tmp_path: Path) -> None:
        """Test scanning nested directories."""
        # Create nested structure
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").write_text("")
        (tmp_path / "pkg" / "module.py").write_text("class Bar: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 2
        assert any(s.name == "Bar" for s in result.symbols)

    def test_scan_excludes_venv(self, tmp_path: Path) -> None:
        """Test that venv directories are excluded by default."""
        (tmp_path / "venv").mkdir()
        (tmp_path / "venv" / "lib.py").write_text("class Excluded: pass")
        (tmp_path / "main.py").write_text("class Included: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1
        assert all(s.name != "Excluded" for s in result.symbols)

    def test_scan_handles_syntax_error(self, tmp_path: Path) -> None:
        """Test that syntax errors are recorded but don't stop scanning."""
        (tmp_path / "good.py").write_text("class Good: pass")
        (tmp_path / "bad.py").write_text("class invalid syntax")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1  # Only good file counted
        assert len(result.errors) == 1
        assert "bad.py" in result.errors[0]

    def test_scan_custom_exclude(self, tmp_path: Path) -> None:
        """Test custom exclude patterns."""
        (tmp_path / "test_foo.py").write_text("class TestFoo: pass")
        (tmp_path / "main.py").write_text("class Main: pass")

        result = scan_directory(tmp_path, exclude_patterns=["**/test_*"])
        assert result.files_scanned == 1
        assert all(s.name != "TestFoo" for s in result.symbols)

    def test_scan_excludes_nested_directories(self, tmp_path: Path) -> None:
        """Test that node_modules and similar nested dirs are excluded."""
        # Source file — should be scanned
        (tmp_path / "main.py").write_text("class Main: pass")

        # Nested node_modules — should be excluded
        nm = tmp_path / "node_modules" / "react"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("function render() {}")

        # Nested .venv — should be excluded
        venv = tmp_path / ".venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "site.py").write_text("class Site: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1
        assert any(s.name == "Main" for s in result.symbols)
        assert not any(s.name == "render" for s in result.symbols)
        assert not any(s.name == "Site" for s in result.symbols)

    def test_scan_excludes_vendor_by_default(self, tmp_path: Path) -> None:
        """Test that vendor directories are excluded by default (PAT-247)."""
        (tmp_path / "main.py").write_text("class Main: pass")

        vendor = tmp_path / "vendor" / "lib"
        vendor.mkdir(parents=True)
        (vendor / "dep.py").write_text("class Dep: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1
        assert any(s.name == "Main" for s in result.symbols)
        assert not any(s.name == "Dep" for s in result.symbols)

    def test_scan_reads_gitignore(self, tmp_path: Path) -> None:
        """Test that .gitignore patterns are merged into exclusions."""
        # .gitignore excludes "vendor"
        (tmp_path / ".gitignore").write_text("vendor\n")

        # Source file
        (tmp_path / "main.py").write_text("class Main: pass")

        # Vendor dir — should be excluded via .gitignore
        vendor = tmp_path / "vendor" / "lib"
        vendor.mkdir(parents=True)
        (vendor / "dep.py").write_text("class Dep: pass")

        result = scan_directory(tmp_path)
        assert result.files_scanned == 1
        assert any(s.name == "Main" for s in result.symbols)
        assert not any(s.name == "Dep" for s in result.symbols)

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning an empty directory."""
        result = scan_directory(tmp_path)
        assert result.files_scanned == 0
        assert result.symbols == []
        assert result.errors == []

    def test_scan_with_language_filter(self, tmp_path: Path) -> None:
        """Test scanning with specific language filter."""
        (tmp_path / "main.py").write_text("class PyClass: pass")
        (tmp_path / "app.ts").write_text("class TsClass {}")

        # Python only
        result = scan_directory(tmp_path, language="python")
        assert result.files_scanned == 1
        assert any(s.name == "PyClass" for s in result.symbols)
        assert not any(s.name == "TsClass" for s in result.symbols)

    def test_scan_auto_detect_mixed(self, tmp_path: Path) -> None:
        """Test auto-detecting languages in mixed codebase."""
        (tmp_path / "main.py").write_text("class PyClass: pass")
        (tmp_path / "app.ts").write_text("class TsClass {}")

        result = scan_directory(tmp_path)  # Auto-detect
        assert result.files_scanned == 2
        assert any(s.name == "PyClass" for s in result.symbols)
        assert any(s.name == "TsClass" for s in result.symbols)

    def test_scan_tsx_files_with_language_filter(self, tmp_path: Path) -> None:
        """Test that .tsx files are found when language=typescript."""
        (tmp_path / "App.tsx").write_text("function App() { return null; }")
        (tmp_path / "utils.ts").write_text("function helper() {}")

        result = scan_directory(tmp_path, language="typescript")
        assert result.files_scanned == 2
        assert any(s.name == "App" for s in result.symbols)
        assert any(s.name == "helper" for s in result.symbols)


class TestExtractTypescriptSymbols:
    """Tests for extract_typescript_symbols function."""

    def test_extract_simple_class(self) -> None:
        """Test extracting a simple TypeScript class."""
        source = dedent("""\
            class MyClass {
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "MyClass"
        assert symbols[0].kind == "class"
        assert symbols[0].line == 1
        assert symbols[0].signature == "class MyClass"

    def test_extract_class_with_extends(self) -> None:
        """Test extracting a class with inheritance."""
        source = dedent("""\
            class UserService extends BaseService {
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert "extends BaseService" in symbols[0].signature

    def test_extract_method(self) -> None:
        """Test extracting methods from a class."""
        source = dedent("""\
            class MyClass {
                myMethod(arg: string): number {
                    return 0;
                }
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 2  # class + method

        method = next(s for s in symbols if s.kind == "method")
        assert method.name == "myMethod"
        assert method.parent == "MyClass"

    def test_extract_function(self) -> None:
        """Test extracting standalone functions."""
        source = dedent("""\
            function processData(data: any[]): void {
                console.log(data);
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "processData"
        assert symbols[0].kind == "function"

    def test_extract_interface(self) -> None:
        """Test extracting TypeScript interfaces."""
        source = dedent("""\
            interface User {
                id: string;
                name: string;
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].kind == "interface"
        assert symbols[0].signature == "interface User"

    def test_extract_complex_file(self) -> None:
        """Test extracting from a file with multiple definitions."""
        source = dedent("""\
            interface Config {
                debug: boolean;
            }

            class Service {
                private config: Config;

                constructor() {}

                process(data: any): void {}
            }

            function helper(): void {}
        """)
        symbols = extract_typescript_symbols(source, "test.ts")

        interfaces = [s for s in symbols if s.kind == "interface"]
        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]
        functions = [s for s in symbols if s.kind == "function"]

        assert len(interfaces) == 1
        assert len(classes) == 1
        assert len(methods) == 2  # constructor + process
        assert len(functions) == 1

    def test_extract_exported_class(self) -> None:
        """Test extracting exported classes."""
        source = dedent("""\
            export class ExportedClass {
                publicMethod(): void {}
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert any(s.name == "ExportedClass" for s in symbols)

    def test_extract_enum(self) -> None:
        """Test extracting TypeScript enums."""
        source = dedent("""\
            export enum UserRole {
                Admin = 'admin',
                User = 'user',
            }
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "UserRole"
        assert symbols[0].kind == "enum"
        assert symbols[0].signature == "enum UserRole"

    def test_extract_type_alias(self) -> None:
        """Test extracting TypeScript type aliases."""
        source = dedent("""\
            export type ReportAction = 'view' | 'edit' | 'delete';
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "ReportAction"
        assert symbols[0].kind == "type_alias"
        assert symbols[0].signature == "type ReportAction"

    def test_extract_exported_const(self) -> None:
        """Test extracting exported const declarations."""
        source = dedent("""\
            export const SESSION_CONFIG = {
                timeout: 30000,
                maxRetries: 3,
            } as const;
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        assert len(symbols) == 1
        assert symbols[0].name == "SESSION_CONFIG"
        assert symbols[0].kind == "constant"
        assert symbols[0].signature == "const SESSION_CONFIG"

    def test_extract_tsx_with_jsx(self) -> None:
        """Test extracting from TSX file with JSX content."""
        source = dedent("""\
            interface UserProps {
                name: string;
            }

            export default function UserCard(props: UserProps) {
                return <div>{props.name}</div>;
            }
        """)
        symbols = extract_typescript_symbols(source, "UserCard.tsx")
        ifaces = [s for s in symbols if s.kind == "interface"]
        funcs = [s for s in symbols if s.kind == "function"]
        assert len(ifaces) == 1
        assert ifaces[0].name == "UserProps"
        assert len(funcs) == 1
        assert funcs[0].name == "UserCard"

    def test_extract_complex_ts_file_with_new_kinds(self) -> None:
        """Test extracting from a file with enums, types, consts, and classes."""
        source = dedent("""\
            export enum Status {
                Active = 'active',
                Inactive = 'inactive',
            }

            export type Config = {
                debug: boolean;
            };

            export const DEFAULT_CONFIG = {
                debug: false,
            };

            export class Service {
                process(): void {}
            }

            export function helper(): void {}
        """)
        symbols = extract_typescript_symbols(source, "test.ts")
        enums = [s for s in symbols if s.kind == "enum"]
        types = [s for s in symbols if s.kind == "type_alias"]
        consts = [s for s in symbols if s.kind == "constant"]
        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]

        assert len(enums) == 1
        assert len(types) == 1
        assert len(consts) == 1
        assert len(classes) == 1
        assert len(functions) == 1


class TestExtractJavascriptSymbols:
    """Tests for extract_javascript_symbols function."""

    def test_extract_class(self) -> None:
        """Test extracting a JavaScript class."""
        source = dedent("""\
            class MyClass {
                constructor() {}
                myMethod() {}
            }
        """)
        symbols = extract_javascript_symbols(source, "test.js")

        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]

        assert len(classes) == 1
        assert len(methods) == 2  # constructor + myMethod

    def test_extract_function(self) -> None:
        """Test extracting JavaScript functions."""
        source = dedent("""\
            function processData(data) {
                return data;
            }
        """)
        symbols = extract_javascript_symbols(source, "test.js")
        assert len(symbols) == 1
        assert symbols[0].name == "processData"
        assert symbols[0].kind == "function"


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_python_extensions(self) -> None:
        """Test Python file extensions."""
        assert detect_language("foo.py") == "python"
        assert detect_language(Path("bar/baz.py")) == "python"

    def test_typescript_extensions(self) -> None:
        """Test TypeScript file extensions."""
        assert detect_language("foo.ts") == "typescript"
        assert detect_language("foo.tsx") == "typescript"

    def test_javascript_extensions(self) -> None:
        """Test JavaScript file extensions."""
        assert detect_language("foo.js") == "javascript"
        assert detect_language("foo.jsx") == "javascript"
        assert detect_language("foo.mjs") == "javascript"
        assert detect_language("foo.cjs") == "javascript"

    def test_php_extensions(self) -> None:
        """Test PHP file extensions."""
        assert detect_language("foo.php") == "php"

    def test_svelte_extensions(self) -> None:
        """Test Svelte file extensions."""
        assert detect_language("foo.svelte") == "svelte"

    def test_csharp_extensions(self) -> None:
        """Test C# file extensions."""
        assert detect_language("foo.cs") == "csharp"

    def test_unsupported_extension(self) -> None:
        """Test unsupported file extensions return None."""
        assert detect_language("foo.rs") is None
        assert detect_language("foo.go") is None
        assert detect_language("foo.txt") is None


class TestExtractSymbols:
    """Tests for the unified extract_symbols function."""

    def test_extract_python(self) -> None:
        """Test extracting Python via unified function."""
        symbols = extract_symbols("class Foo: pass", "test.py", "python")
        assert symbols[0].name == "Foo"

    def test_extract_typescript(self) -> None:
        """Test extracting TypeScript via unified function."""
        symbols = extract_symbols("class Foo {}", "test.ts", "typescript")
        assert symbols[0].name == "Foo"

    def test_extract_javascript(self) -> None:
        """Test extracting JavaScript via unified function."""
        symbols = extract_symbols("class Foo {}", "test.js", "javascript")
        assert symbols[0].name == "Foo"

    def test_extract_php(self) -> None:
        """Test extracting PHP via unified function."""
        source = "<?php\nclass Foo {}"
        symbols = extract_symbols(source, "test.php", "php")
        assert symbols[0].name == "Foo"
        assert symbols[0].kind == "class"

    def test_extract_csharp(self) -> None:
        """Test extracting C# via unified function."""
        source = "class Foo {}"
        symbols = extract_symbols(source, "test.cs", "csharp")
        assert symbols[0].name == "Foo"
        assert symbols[0].kind == "class"

    def test_unsupported_language_raises(self) -> None:
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            extract_symbols("fn main() {}", "test.rs", "rust")  # type: ignore[arg-type]


class TestExtractPhpSymbols:
    """Tests for extract_php_symbols function."""

    def test_extract_class(self) -> None:
        """Test extracting a PHP class."""
        source = dedent("""\
            <?php
            class User {
                public function getName(): string {
                    return $this->name;
                }
            }
        """)
        symbols = extract_php_symbols(source, "User.php")
        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]
        assert len(classes) == 1
        assert classes[0].name == "User"
        assert classes[0].signature == "class User"
        assert len(methods) == 1
        assert methods[0].name == "getName"
        assert methods[0].parent == "User"

    def test_extract_class_with_extends_implements(self) -> None:
        """Test extracting class with inheritance."""
        source = dedent("""\
            <?php
            class User extends Model implements Configurable {
            }
        """)
        symbols = extract_php_symbols(source, "User.php")
        assert len(symbols) == 1
        assert symbols[0].kind == "class"
        assert "extends Model" in symbols[0].signature
        assert "implements Configurable" in symbols[0].signature

    def test_extract_interface(self) -> None:
        """Test extracting a PHP interface."""
        source = dedent("""\
            <?php
            interface Configurable {
                public function getConfig(): array;
            }
        """)
        symbols = extract_php_symbols(source, "Configurable.php")
        ifaces = [s for s in symbols if s.kind == "interface"]
        methods = [s for s in symbols if s.kind == "method"]
        assert len(ifaces) == 1
        assert ifaces[0].name == "Configurable"
        assert ifaces[0].signature == "interface Configurable"
        assert len(methods) == 1
        assert methods[0].parent == "Configurable"

    def test_extract_trait(self) -> None:
        """Test extracting a PHP trait."""
        source = dedent("""\
            <?php
            trait HasSlug {
                public function getSlug(): string {
                    return 'slug';
                }
            }
        """)
        symbols = extract_php_symbols(source, "HasSlug.php")
        traits = [s for s in symbols if s.kind == "trait"]
        methods = [s for s in symbols if s.kind == "method"]
        assert len(traits) == 1
        assert traits[0].name == "HasSlug"
        assert traits[0].signature == "trait HasSlug"
        assert len(methods) == 1
        assert methods[0].parent == "HasSlug"

    def test_extract_function(self) -> None:
        """Test extracting a top-level PHP function."""
        source = dedent("""\
            <?php
            function helper(int $x): int {
                return $x * 2;
            }
        """)
        symbols = extract_php_symbols(source, "helpers.php")
        assert len(symbols) == 1
        assert symbols[0].kind == "function"
        assert symbols[0].name == "helper"
        assert "function helper" in symbols[0].signature

    def test_extract_enum(self) -> None:
        """Test extracting a PHP 8.1 enum."""
        source = dedent("""\
            <?php
            enum Status: string {
                case Active = 'active';
                case Inactive = 'inactive';
            }
        """)
        symbols = extract_php_symbols(source, "Status.php")
        assert len(symbols) == 1
        assert symbols[0].kind == "enum"
        assert symbols[0].name == "Status"
        assert "enum Status" in symbols[0].signature

    def test_extract_with_namespace(self) -> None:
        """Test that namespace qualifies symbol names."""
        source = dedent("""\
            <?php
            namespace App\\Models;

            class User {
                public function getName(): string {
                    return $this->name;
                }
            }

            function helper(): void {}
        """)
        symbols = extract_php_symbols(source, "User.php")
        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]
        methods = [s for s in symbols if s.kind == "method"]
        assert classes[0].name == "App.Models.User"
        assert functions[0].name == "App.Models.helper"
        # Methods keep local name with parent reference
        assert methods[0].name == "getName"
        assert methods[0].parent == "App.Models.User"

    def test_method_visibility_in_signature(self) -> None:
        """Test that method signature includes visibility modifier."""
        source = dedent("""\
            <?php
            class Foo {
                public function bar(): void {}
                private function baz(): void {}
                protected static function qux(): void {}
            }
        """)
        symbols = extract_php_symbols(source, "Foo.php")
        methods = [s for s in symbols if s.kind == "method"]
        assert len(methods) == 3
        sigs = {m.name: m.signature for m in methods}
        assert "public" in sigs["bar"]
        assert "private" in sigs["baz"]
        assert "protected" in sigs["qux"]
        assert "static" in sigs["qux"]

    def test_complex_php_file(self) -> None:
        """Test extracting from a file with multiple construct types."""
        source = dedent("""\
            <?php
            namespace App\\Services;

            interface ServiceContract {
                public function execute(): void;
            }

            trait Loggable {
                public function log(string $msg): void {}
            }

            class UserService implements ServiceContract {
                use Loggable;

                public function execute(): void {}
                private function validate(): bool { return true; }
            }

            function createService(): ServiceContract {
                return new UserService();
            }

            enum Priority: int {
                case Low = 1;
                case High = 2;
            }
        """)
        symbols = extract_php_symbols(source, "UserService.php")
        ifaces = [s for s in symbols if s.kind == "interface"]
        traits = [s for s in symbols if s.kind == "trait"]
        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]
        methods = [s for s in symbols if s.kind == "method"]
        enums = [s for s in symbols if s.kind == "enum"]

        assert len(ifaces) == 1
        assert ifaces[0].name == "App.Services.ServiceContract"
        assert len(traits) == 1
        assert traits[0].name == "App.Services.Loggable"
        assert len(classes) == 1
        assert classes[0].name == "App.Services.UserService"
        assert len(functions) == 1
        assert functions[0].name == "App.Services.createService"
        assert len(enums) == 1
        assert enums[0].name == "App.Services.Priority"
        # 1 interface method + 1 trait method + 2 class methods
        assert len(methods) == 4

    def test_empty_php_file(self) -> None:
        """Test that an empty PHP file doesn't crash."""
        source = "<?php\n"
        symbols = extract_php_symbols(source, "empty.php")
        assert symbols == []

    def test_php_only_namespace_and_use(self) -> None:
        """Test PHP file with only namespace and use statements."""
        source = dedent("""\
            <?php
            namespace App\\Models;

            use Illuminate\\Database\\Eloquent\\Model;
        """)
        symbols = extract_php_symbols(source, "imports.php")
        assert symbols == []

    def test_blade_php_excluded_from_scan(self, tmp_path: Path) -> None:
        """Test that .blade.php files are excluded from PHP scan."""
        # Create a regular PHP file
        php_file = tmp_path / "User.php"
        php_file.write_text("<?php\nclass User {}\n")

        # Create a blade template
        blade_file = tmp_path / "welcome.blade.php"
        blade_file.write_text("<html><body>{{ $name }}</body></html>\n")

        result = scan_directory(tmp_path, language="php")
        names = [s.name for s in result.symbols]
        assert "User" in names
        # Blade file should be explicitly skipped — only 1 file scanned
        assert result.files_scanned == 1
        assert len(result.errors) == 0


class TestExtractSvelteSymbols:
    """Tests for extract_svelte_symbols function."""

    def test_extract_js_script_block(self) -> None:
        """Test extracting symbols from a JS script block."""
        source = dedent("""\
            <script>
              function greet(msg) {
                return 'Hello ' + msg;
              }

              class UserService {
                getName() {
                  return this.name;
                }
              }
            </script>

            <h1>Hello</h1>
        """)
        symbols = extract_svelte_symbols(source, "Greeting.svelte")
        component = [s for s in symbols if s.kind == "component"]
        functions = [s for s in symbols if s.kind == "function"]
        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]

        assert len(component) == 1
        assert component[0].name == "Greeting"
        assert component[0].signature == "component Greeting"
        assert component[0].line == 1

        assert len(functions) == 1
        assert functions[0].name == "greet"

        assert len(classes) == 1
        assert classes[0].name == "UserService"

        assert len(methods) == 1
        assert methods[0].name == "getName"
        assert methods[0].parent == "UserService"

    def test_extract_ts_script_block(self) -> None:
        """Test extracting symbols from a TypeScript script block."""
        source = dedent("""\
            <script lang="ts">
              interface User {
                name: string;
              }

              export function getUser(): User {
                return { name: 'test' };
              }
            </script>

            <div>Hello</div>
        """)
        symbols = extract_svelte_symbols(source, "UserCard.svelte")
        component = [s for s in symbols if s.kind == "component"]
        interfaces = [s for s in symbols if s.kind == "interface"]
        functions = [s for s in symbols if s.kind == "function"]

        assert len(component) == 1
        assert component[0].name == "UserCard"

        assert len(interfaces) == 1
        assert interfaces[0].name == "User"

        assert len(functions) == 1
        assert functions[0].name == "getUser"

    def test_no_script_block(self) -> None:
        """Test that a file with no script block returns component only."""
        source = "<div>Static content only</div>\n"
        symbols = extract_svelte_symbols(source, "Static.svelte")
        assert len(symbols) == 1
        assert symbols[0].kind == "component"
        assert symbols[0].name == "Static"

    def test_empty_script_block(self) -> None:
        """Test that an empty script block returns component only."""
        source = "<script></script>\n<div>Hello</div>\n"
        symbols = extract_svelte_symbols(source, "Empty.svelte")
        assert len(symbols) == 1
        assert symbols[0].kind == "component"
        assert symbols[0].name == "Empty"

    def test_line_numbers_offset(self) -> None:
        """Test that line numbers are correct relative to the .svelte file."""
        source = dedent("""\
            <script>
              function first() {}

              function second() {}
            </script>
        """)
        symbols = extract_svelte_symbols(source, "Lines.svelte")
        functions = [s for s in symbols if s.kind == "function"]
        assert len(functions) == 2
        # first() is on line 2 of the .svelte file
        assert functions[0].name == "first"
        assert functions[0].line == 2
        # second() is on line 4 of the .svelte file
        assert functions[1].name == "second"
        assert functions[1].line == 4

    def test_component_name_from_filename(self) -> None:
        """Test that component name is derived from filename stem."""
        source = "<div>Hello</div>\n"
        symbols = extract_svelte_symbols(source, "src/lib/MyComponent.svelte")
        assert symbols[0].name == "MyComponent"
        assert symbols[0].file == "src/lib/MyComponent.svelte"

    def test_extract_svelte_via_unified(self) -> None:
        """Test extracting Svelte via unified extract_symbols function."""
        source = dedent("""\
            <script>
              function hello() {}
            </script>
        """)
        symbols = extract_symbols(source, "App.svelte", "svelte")
        component = [s for s in symbols if s.kind == "component"]
        functions = [s for s in symbols if s.kind == "function"]
        assert len(component) == 1
        assert component[0].name == "App"
        assert len(functions) == 1
        assert functions[0].name == "hello"

    def test_script_context_module(self) -> None:
        """Test extracting from both instance and module script blocks."""
        source = dedent("""\
            <script context="module">
              export function shared() {}
            </script>

            <script>
              function instance() {}
            </script>

            <div>Hello</div>
        """)
        symbols = extract_svelte_symbols(source, "Dual.svelte")
        functions = [s for s in symbols if s.kind == "function"]
        names = {f.name for f in functions}
        assert "shared" in names
        assert "instance" in names

    def test_scan_directory_svelte(self, tmp_path: Path) -> None:
        """Test scan_directory finds and parses .svelte files."""
        svelte_file = tmp_path / "Counter.svelte"
        svelte_file.write_text(
            dedent("""\
            <script>
              let count = 0;

              function increment() {
                count += 1;
              }
            </script>

            <button on:click={increment}>{count}</button>
        """)
        )

        # Also add a non-svelte file to ensure it's not picked up
        other_file = tmp_path / "utils.js"
        other_file.write_text("function helper() {}\n")

        result = scan_directory(tmp_path, language="svelte")
        assert result.files_scanned == 1
        assert len(result.errors) == 0

        components = [s for s in result.symbols if s.kind == "component"]
        functions = [s for s in result.symbols if s.kind == "function"]
        assert len(components) == 1
        assert components[0].name == "Counter"
        assert len(functions) == 1
        assert functions[0].name == "increment"


class TestExtractCsharpSymbols:
    """Tests for extract_csharp_symbols function."""

    def test_extract_class(self) -> None:
        """Test extracting a C# class."""
        source = dedent("""\
            public class UserService {
                public void Process() { }
            }
        """)
        symbols = extract_csharp_symbols(source, "UserService.cs")
        classes = [s for s in symbols if s.kind == "class"]
        methods = [s for s in symbols if s.kind == "method"]
        assert len(classes) == 1
        assert classes[0].name == "UserService"
        assert classes[0].signature == "class UserService"
        assert len(methods) == 1
        assert methods[0].name == "Process"
        assert methods[0].parent == "UserService"

    def test_extract_class_with_inheritance(self) -> None:
        """Test extracting a class with base class and interfaces."""
        source = dedent("""\
            public class UserService : BaseService, IUserService {
            }
        """)
        symbols = extract_csharp_symbols(source, "UserService.cs")
        assert len(symbols) == 1
        assert symbols[0].kind == "class"
        assert "UserService" in symbols[0].signature
        assert ": BaseService, IUserService" in symbols[0].signature

    def test_extract_interface(self) -> None:
        """Test extracting a C# interface."""
        source = dedent("""\
            public interface IUserService {
                Task<User> GetUserAsync(int id);
            }
        """)
        symbols = extract_csharp_symbols(source, "IUserService.cs")
        ifaces = [s for s in symbols if s.kind == "interface"]
        methods = [s for s in symbols if s.kind == "method"]
        assert len(ifaces) == 1
        assert ifaces[0].name == "IUserService"
        assert ifaces[0].signature == "interface IUserService"
        assert len(methods) == 1
        assert methods[0].name == "GetUserAsync"
        assert methods[0].parent == "IUserService"

    def test_extract_struct(self) -> None:
        """Test extracting a C# struct (maps to class kind)."""
        source = dedent("""\
            public struct Point {
                public int X { get; set; }
                public int Y { get; set; }
            }
        """)
        symbols = extract_csharp_symbols(source, "Point.cs")
        structs = [s for s in symbols if s.kind == "class"]
        props = [s for s in symbols if s.kind == "method"]
        assert len(structs) == 1
        assert structs[0].name == "Point"
        assert "struct Point" in structs[0].signature
        assert len(props) == 2

    def test_extract_record(self) -> None:
        """Test extracting a C# record (maps to class kind)."""
        source = "public record UserDto(string Name, string Email);\n"
        symbols = extract_csharp_symbols(source, "UserDto.cs")
        assert len(symbols) == 1
        assert symbols[0].kind == "class"
        assert symbols[0].name == "UserDto"
        assert "record UserDto" in symbols[0].signature

    def test_extract_enum(self) -> None:
        """Test extracting a C# enum."""
        source = dedent("""\
            public enum UserRole {
                Admin,
                User,
                Guest
            }
        """)
        symbols = extract_csharp_symbols(source, "UserRole.cs")
        assert len(symbols) == 1
        assert symbols[0].kind == "enum"
        assert symbols[0].name == "UserRole"
        assert "enum UserRole" in symbols[0].signature

    def test_extract_property(self) -> None:
        """Test extracting properties (maps to method kind)."""
        source = dedent("""\
            public class Config {
                public string ConnectionString { get; set; }
                private int MaxRetries { get; }
            }
        """)
        symbols = extract_csharp_symbols(source, "Config.cs")
        props = [s for s in symbols if s.kind == "method" and s.parent == "Config"]
        assert len(props) == 2
        assert props[0].name == "ConnectionString"
        assert props[1].name == "MaxRetries"

    def test_extract_with_namespace(self) -> None:
        """Test that namespace does NOT qualify symbol names — local name only (RAISE-226)."""
        source = dedent("""\
            namespace MyApp.Services
            {
                public class UserService {
                    public void Process() { }
                }

                public interface IService { }

                public enum Priority {
                    Low,
                    High
                }
            }
        """)
        symbols = extract_csharp_symbols(source, "UserService.cs")
        classes = [s for s in symbols if s.kind == "class"]
        ifaces = [s for s in symbols if s.kind == "interface"]
        enums = [s for s in symbols if s.kind == "enum"]
        methods = [s for s in symbols if s.kind == "method"]
        assert classes[0].name == "UserService"
        assert ifaces[0].name == "IService"
        assert enums[0].name == "Priority"
        assert methods[0].name == "Process"
        assert methods[0].parent == "UserService"

    def test_method_visibility_in_signature(self) -> None:
        """Test that method signature includes visibility modifiers."""
        source = dedent("""\
            public class Foo {
                public void Bar() { }
                private int Baz() { return 0; }
                protected static void Qux() { }
            }
        """)
        symbols = extract_csharp_symbols(source, "Foo.cs")
        methods = [s for s in symbols if s.kind == "method"]
        assert len(methods) == 3
        sigs = {m.name: m.signature for m in methods}
        assert "public" in sigs["Bar"]
        assert "private" in sigs["Baz"]
        assert "protected" in sigs["Qux"]
        assert "static" in sigs["Qux"]

    def test_complex_csharp_file(self) -> None:
        """Test extracting from a file with multiple construct types."""
        source = dedent("""\
            namespace MyApp.Services
            {
                public interface IUserService {
                    Task<User> GetUserAsync(int id);
                }

                public class UserService : IUserService {
                    public string ConnectionString { get; set; }

                    public async Task<User> GetUserAsync(int id) {
                        return null;
                    }

                    private void ValidateId(int id) { }
                }

                public enum UserRole {
                    Admin,
                    User,
                    Guest
                }

                public record UserDto(string Name, string Email);

                public struct Point {
                    public int X { get; set; }
                    public int Y { get; set; }
                }
            }
        """)
        symbols = extract_csharp_symbols(source, "Service.cs")
        ifaces = [s for s in symbols if s.kind == "interface"]
        classes = [s for s in symbols if s.kind == "class"]
        enums = [s for s in symbols if s.kind == "enum"]
        methods = [s for s in symbols if s.kind == "method"]

        assert len(ifaces) == 1
        assert ifaces[0].name == "IUserService"
        # UserService + UserDto (record) + Point (struct)
        assert len(classes) == 3
        assert len(enums) == 1
        assert enums[0].name == "UserRole"
        # IUserService.GetUserAsync + UserService.(ConnectionString, GetUserAsync, ValidateId) + Point.(X, Y)
        assert len(methods) == 6

    def test_empty_csharp_file(self) -> None:
        """Test that an empty C# file doesn't crash."""
        source = "using System;\n"
        symbols = extract_csharp_symbols(source, "empty.cs")
        assert symbols == []

    def test_constructor_deps_extracted(self) -> None:
        """Regression RAISE-227: constructor parameter types populate depends_on."""
        source = dedent("""\
            public class OrderHandler {
                private readonly IOrderRepository _repo;
                private readonly IValidator _validator;

                public OrderHandler(IOrderRepository repo, IValidator validator) {
                    _repo = repo;
                    _validator = validator;
                }

                public void Handle() { }
            }
        """)
        symbols = extract_csharp_symbols(source, "OrderHandler.cs")
        classes = [s for s in symbols if s.kind == "class"]
        assert len(classes) == 1
        assert set(classes[0].depends_on) == {"IOrderRepository", "IValidator"}

    def test_constructor_deps_no_params(self) -> None:
        """Class with parameterless constructor has empty depends_on."""
        source = dedent("""\
            public class SimpleService {
                public SimpleService() { }
                public void Run() { }
            }
        """)
        symbols = extract_csharp_symbols(source, "SimpleService.cs")
        classes = [s for s in symbols if s.kind == "class"]
        assert len(classes) == 1
        assert classes[0].depends_on == []

    def test_constructor_deps_excludes_primitives(self) -> None:
        """Primitive types (string, int, bool) are excluded from depends_on."""
        source = dedent("""\
            public class Config {
                public Config(string connectionString, int timeout, bool enableCache) { }
            }
        """)
        symbols = extract_csharp_symbols(source, "Config.cs")
        classes = [s for s in symbols if s.kind == "class"]
        assert len(classes) == 1
        assert classes[0].depends_on == []

    def test_designer_cs_excluded_from_scan(self, tmp_path: Path) -> None:
        """Test that .Designer.cs files are excluded from C# scan."""
        cs_file = tmp_path / "Form1.cs"
        cs_file.write_text("public class Form1 {}\n")

        designer_file = tmp_path / "Form1.Designer.cs"
        designer_file.write_text(
            "public partial class Form1 { private void InitializeComponent() {} }\n"
        )

        result = scan_directory(tmp_path, language="csharp")
        names = [s.name for s in result.symbols]
        assert "Form1" in names
        assert result.files_scanned == 1
        assert len(result.errors) == 0

    def test_scan_directory_csharp(self, tmp_path: Path) -> None:
        """Test scan_directory finds and parses .cs files."""
        cs_file = tmp_path / "UserService.cs"
        cs_file.write_text(
            dedent("""\
            namespace MyApp {
                public class UserService {
                    public void Process() { }
                }
            }
        """)
        )

        other_file = tmp_path / "main.py"
        other_file.write_text("class Main: pass\n")

        result = scan_directory(tmp_path, language="csharp")
        assert result.files_scanned == 1
        assert any(s.name == "UserService" for s in result.symbols)
        assert not any(s.name == "Main" for s in result.symbols)


class TestReadGitignore:
    """Regression tests for _read_gitignore (RAISE-534)."""

    def test_bare_name_gets_double_star_prefix(self, tmp_path: Path) -> None:
        """Bare names like 'node_modules' match anywhere: **/node_modules/**."""
        (tmp_path / ".gitignore").write_text("node_modules\n")
        patterns = _read_gitignore(tmp_path)
        assert patterns == ["**/node_modules/**"]

    def test_path_entry_no_double_star_prefix(self, tmp_path: Path) -> None:
        """Entries with '/' are path-relative: should NOT get **/ prefix."""
        (tmp_path / ".gitignore").write_text("build/output\n")
        patterns = _read_gitignore(tmp_path)
        assert patterns == ["build/output/**"]

    def test_mixed_entries(self, tmp_path: Path) -> None:
        """Bare and path entries produce distinct patterns."""
        (tmp_path / ".gitignore").write_text("__pycache__\ndist/assets\n")
        patterns = _read_gitignore(tmp_path)
        assert patterns == ["**/__pycache__/**", "dist/assets/**"]
