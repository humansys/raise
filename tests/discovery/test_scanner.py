"""Tests for code scanner (Python, TypeScript, JavaScript)."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.discovery.scanner import (
    ScanResult,
    Symbol,
    detect_language,
    extract_javascript_symbols,
    extract_python_symbols,
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

    def test_unsupported_language_raises(self) -> None:
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            extract_symbols("fn main() {}", "test.rs", "rust")  # type: ignore[arg-type]
