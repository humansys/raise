"""Code scanner for symbol extraction.

This module extracts classes, functions, and module-level information
from source files. Supports:
- Python (via built-in ast module)
- TypeScript/JavaScript (via tree-sitter)

Example:
    >>> from raise_cli.discovery.scanner import extract_python_symbols
    >>> symbols = extract_python_symbols("class Foo: pass", "example.py")
    >>> symbols[0].name
    'Foo'
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from tree_sitter import Node, Parser

# Symbol kinds that can be extracted
SymbolKind = Literal["class", "function", "method", "module", "interface"]

# Supported languages for scanning
Language = Literal["python", "typescript", "javascript"]

# File extension to language mapping
EXTENSION_TO_LANGUAGE: dict[str, Language] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}


class Symbol(BaseModel):
    """A code symbol extracted from source.

    Attributes:
        name: Symbol name (e.g., "UserService", "get_user").
        kind: Symbol type (class, function, method, module).
        file: Relative path to source file.
        line: Line number where symbol is defined (1-indexed).
        signature: Full signature (e.g., "class UserService(BaseService)").
        docstring: Symbol's docstring if present.
        parent: Parent symbol name for methods (e.g., class name).

    Examples:
        >>> symbol = Symbol(
        ...     name="UserService",
        ...     kind="class",
        ...     file="src/services/user.py",
        ...     line=15,
        ...     signature="class UserService(BaseService)",
        ... )
        >>> symbol.name
        'UserService'
    """

    name: str = Field(..., description="Symbol name")
    kind: SymbolKind = Field(..., description="Symbol type")
    file: str = Field(..., description="Relative path to source file")
    line: int = Field(..., description="Line number (1-indexed)")
    signature: str = Field(default="", description="Full signature")
    docstring: str | None = Field(default=None, description="Symbol docstring")
    parent: str | None = Field(default=None, description="Parent symbol name")


class ScanResult(BaseModel):
    """Result of scanning a directory or file.

    Attributes:
        symbols: List of extracted symbols.
        files_scanned: Number of files processed.
        errors: List of files that failed to parse.

    Examples:
        >>> result = ScanResult(symbols=[], files_scanned=5, errors=[])
        >>> result.files_scanned
        5
    """

    symbols: list[Symbol] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    files_scanned: int = Field(default=0)
    errors: list[str] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]


def _get_signature(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Extract signature from an AST node.

    Args:
        node: AST node for class or function definition.

    Returns:
        Signature string (e.g., "class Foo(Bar)" or "def func(a, b)").
    """
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(base) for base in node.bases)
        if bases:
            return f"class {node.name}({bases})"
        return f"class {node.name}"

    # FunctionDef or AsyncFunctionDef
    args_str = ast.unparse(node.args)
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"

    if node.returns:
        return_annotation = ast.unparse(node.returns)
        return f"{prefix} {node.name}({args_str}) -> {return_annotation}"
    return f"{prefix} {node.name}({args_str})"


def _extract_module_symbol(tree: ast.Module, file_path: str) -> Symbol | None:
    """Extract module-level symbol if docstring exists."""
    module_docstring = ast.get_docstring(tree)
    if not module_docstring:
        return None
    return Symbol(
        name=Path(file_path).stem,
        kind="module",
        file=file_path,
        line=1,
        signature=f"module {Path(file_path).stem}",
        docstring=module_docstring,
    )


def _extract_class_symbols(node: ast.ClassDef, file_path: str) -> list[Symbol]:
    """Extract class and its methods as symbols."""
    symbols: list[Symbol] = [
        Symbol(
            name=node.name,
            kind="class",
            file=file_path,
            line=node.lineno,
            signature=_get_signature(node),
            docstring=ast.get_docstring(node),
        )
    ]
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                Symbol(
                    name=item.name,
                    kind="method",
                    file=file_path,
                    line=item.lineno,
                    signature=_get_signature(item),
                    docstring=ast.get_docstring(item),
                    parent=node.name,
                )
            )
    return symbols


def extract_python_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from Python source code.

    Parses the source code and extracts all classes, functions, and methods
    with their signatures and docstrings.

    Args:
        source: Python source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Raises:
        SyntaxError: If source code cannot be parsed.

    Examples:
        >>> source = '''
        ... class MyClass:
        ...     \"\"\"A sample class.\"\"\"
        ...     def method(self):
        ...         pass
        ... '''
        >>> symbols = extract_python_symbols(source, "example.py")
        >>> len(symbols)
        2
        >>> symbols[0].kind
        'class'
    """
    tree = ast.parse(source)
    symbols: list[Symbol] = []

    # Module docstring
    module_symbol = _extract_module_symbol(tree, file_path)
    if module_symbol:
        symbols.append(module_symbol)

    # Classes and their methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.extend(_extract_class_symbols(node, file_path))

    # Top-level functions (separate pass to avoid duplicates with methods)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                Symbol(
                    name=node.name,
                    kind="function",
                    file=file_path,
                    line=node.lineno,
                    signature=_get_signature(node),
                    docstring=ast.get_docstring(node),
                )
            )

    return symbols


# -----------------------------------------------------------------------------
# TypeScript/JavaScript Extraction (tree-sitter)
# -----------------------------------------------------------------------------


def _get_ts_parser(language: Language) -> Parser:
    """Get a tree-sitter parser for TypeScript or JavaScript.

    Args:
        language: Either "typescript" or "javascript".

    Returns:
        Configured tree-sitter Parser.

    Raises:
        ImportError: If tree-sitter packages are not installed.
    """
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for TypeScript/JavaScript scanning. "
            "Install with: uv add tree-sitter tree-sitter-typescript tree-sitter-javascript"
        ) from e

    if language == "typescript":
        import tree_sitter_typescript as ts_typescript

        lang = TSLanguage(ts_typescript.language_typescript())
    else:
        import tree_sitter_javascript as ts_javascript

        lang = TSLanguage(ts_javascript.language())

    return Parser(lang)


def _find_child_by_type(node: Node, *types: str) -> Node | None:
    """Find the first child node matching any of the given types."""
    for child in node.children:
        if child.type in types:
            return child
    return None


def _get_node_text(node: Node, source: bytes) -> str:
    """Get the text content of a tree-sitter node."""
    return source[node.start_byte : node.end_byte].decode("utf-8")


def _extract_ts_signature(node: Node, source: bytes) -> str:
    """Extract a signature from a TypeScript/JavaScript AST node."""
    node_type = node.type

    if node_type == "class_declaration":
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        # Check for extends
        heritage = _find_child_by_type(node, "class_heritage")
        if heritage:
            return f"class {name} {_get_node_text(heritage, source)}"
        return f"class {name}"

    elif node_type in ("function_declaration", "generator_function_declaration"):
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        # Check for return type annotation
        return_type = _find_child_by_type(node, "type_annotation")
        if return_type:
            return f"function {name}{params}{_get_node_text(return_type, source)}"
        return f"function {name}{params}"

    elif node_type in ("method_definition", "method_signature"):
        name_node = _find_child_by_type(node, "property_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        return f"{name}{params}"

    elif node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    return ""


def extract_typescript_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from TypeScript source code.

    Uses tree-sitter to parse TypeScript and extract classes, functions,
    methods, and interfaces.

    Args:
        source: TypeScript source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... export class MyClass {
        ...     myMethod(): void {}
        ... }
        ... '''
        >>> symbols = extract_typescript_symbols(source, "example.ts")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_ts_parser("typescript")
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return _extract_ts_js_symbols(tree.root_node, source_bytes, file_path)


def extract_javascript_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from JavaScript source code.

    Uses tree-sitter to parse JavaScript and extract classes, functions,
    and methods.

    Args:
        source: JavaScript source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... class MyClass {
        ...     myMethod() {}
        ... }
        ... '''
        >>> symbols = extract_javascript_symbols(source, "example.js")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_ts_parser("javascript")
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return _extract_ts_js_symbols(tree.root_node, source_bytes, file_path)


def _extract_ts_js_symbols(
    root: Node,
    source: bytes,
    file_path: str,
) -> list[Symbol]:
    """Extract symbols from a tree-sitter parse tree.

    Walks the AST and extracts classes, functions, methods, and interfaces.

    Args:
        root: Root node of the tree-sitter parse tree.
        source: Source code as bytes.
        file_path: Path to the source file.

    Returns:
        List of Symbol objects.
    """
    symbols: list[Symbol] = []

    # Node types we care about
    class_types = {"class_declaration"}
    function_types = {"function_declaration", "generator_function_declaration"}
    method_types = {"method_definition", "method_signature"}
    interface_types = {"interface_declaration"}

    def walk(node: Node, parent_class: str | None = None) -> None:
        node_type = node.type

        if node_type in class_types:
            name_node = _find_child_by_type(node, "type_identifier", "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="class",
                    file=file_path,
                    line=node.start_point[0] + 1,  # tree-sitter is 0-indexed
                    signature=_extract_ts_signature(node, source),
                )
            )

            # Walk class body for methods
            body = _find_child_by_type(node, "class_body")
            if body:
                for child in body.children:
                    walk(child, parent_class=name)
            return  # Don't recurse further into class

        elif node_type in function_types and parent_class is None:
            name_node = _find_child_by_type(node, "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="function",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_ts_signature(node, source),
                )
            )

        elif node_type in method_types and parent_class is not None:
            name_node = _find_child_by_type(node, "property_identifier", "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="method",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_ts_signature(node, source),
                    parent=parent_class,
                )
            )

        elif node_type in interface_types:
            name_node = _find_child_by_type(node, "type_identifier", "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="interface",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_ts_signature(node, source),
                )
            )

        # Recurse into children
        for child in node.children:
            walk(child, parent_class)

    walk(root)
    return symbols


def detect_language(file_path: str | Path) -> Language | None:
    """Detect language from file extension.

    Args:
        file_path: Path to the file.

    Returns:
        Language literal or None if not supported.

    Examples:
        >>> detect_language("foo.py")
        'python'
        >>> detect_language("bar.ts")
        'typescript'
        >>> detect_language("baz.rs")  # Returns None
    """
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext)


def extract_symbols(source: str, file_path: str, language: Language) -> list[Symbol]:
    """Extract symbols from source code in any supported language.

    Args:
        source: Source code as string.
        file_path: Path to the source file (for metadata).
        language: Language of the source code.

    Returns:
        List of Symbol objects.

    Raises:
        ValueError: If language is not supported.
        SyntaxError: If source code cannot be parsed (Python only).

    Examples:
        >>> symbols = extract_symbols("class Foo: pass", "foo.py", "python")
        >>> symbols[0].kind
        'class'
    """
    if language == "python":
        return extract_python_symbols(source, file_path)
    elif language == "typescript":
        return extract_typescript_symbols(source, file_path)
    elif language == "javascript":
        return extract_javascript_symbols(source, file_path)
    else:
        raise ValueError(f"Unsupported language: {language}")


# Default patterns to exclude when scanning directories
DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**",
    "**/.git/**",
]

# Language-specific default glob patterns
DEFAULT_LANGUAGE_PATTERNS: dict[Language | None, str] = {
    "python": "**/*.py",
    "typescript": "**/*.ts",
    "javascript": "**/*.js",
    None: "**/*",  # Auto-detect: scan all files
}


def _should_exclude(file_path: Path, exclude_patterns: list[str]) -> bool:
    """Check if a file should be excluded based on patterns."""
    return any(file_path.match(pattern) for pattern in exclude_patterns)


def _process_source_file(
    file_path: Path, rel_str: str, language: Language, result: ScanResult
) -> None:
    """Extract symbols from a source file and update result."""
    try:
        source = file_path.read_text(encoding="utf-8")
        symbols = extract_symbols(source, rel_str, language)
        result.symbols.extend(symbols)
        result.files_scanned += 1
    except SyntaxError as e:
        result.errors.append(f"{rel_str}: {e}")
    except UnicodeDecodeError as e:
        result.errors.append(f"{rel_str}: {e}")
    except Exception as e:
        result.errors.append(f"{rel_str}: {e}")


def scan_directory(
    path: Path,
    *,
    language: Language | None = None,
    pattern: str | None = None,
    exclude_patterns: list[str] | None = None,
) -> ScanResult:
    """Scan a directory for code symbols.

    Recursively walks the directory, extracts symbols from source files,
    and returns aggregated results. Supports Python, TypeScript, and JavaScript.

    Args:
        path: Directory path to scan.
        language: Language to scan for. If None, auto-detects from extensions.
        pattern: Glob pattern for files. If None, uses language-specific default.
        exclude_patterns: List of patterns to exclude (e.g., ["**/test_*"]).

    Returns:
        ScanResult with all extracted symbols.

    Examples:
        >>> result = scan_directory(Path("src/"))  # Auto-detect
        >>> result = scan_directory(Path("src/"), language="typescript")
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    if pattern is None:
        pattern = DEFAULT_LANGUAGE_PATTERNS.get(language, "**/*")

    result = ScanResult()
    root = path.resolve()

    for file_path in path.glob(pattern):
        if file_path.is_dir():
            continue

        if _should_exclude(file_path, exclude_patterns):
            continue

        rel_path = (
            file_path.relative_to(root) if file_path.is_relative_to(root) else file_path
        )
        rel_str = str(rel_path)

        file_language = language or detect_language(file_path)
        if file_language is None:
            continue

        _process_source_file(file_path, rel_str, file_language, result)

    return result
