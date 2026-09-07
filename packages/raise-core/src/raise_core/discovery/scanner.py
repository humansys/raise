"""Code scanner for symbol extraction.

This module extracts classes, functions, and module-level information
from source files. Supports:
- Python (via built-in ast module)
- TypeScript/JavaScript (via tree-sitter)

Example:
    >>> from raise_core.discovery.scanner import extract_python_symbols
    >>> symbols = extract_python_symbols("class Foo: pass", "example.py")
    >>> symbols[0].name
    'Foo'
"""

from __future__ import annotations

import ast
import bisect
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NamedTuple

from pydantic import BaseModel, Field

from raise_core.compat import portable_path

if TYPE_CHECKING:
    from tree_sitter import Node, Parser

# Symbol kinds that can be extracted
SymbolKind = Literal[
    "class",
    "function",
    "method",
    "module",
    "interface",
    "enum",
    "type_alias",
    "constant",
    "trait",
    "component",
]

# Supported languages for scanning
Language = Literal[
    "python",
    "typescript",
    "javascript",
    "php",
    "svelte",
    "csharp",
    "dart",
    "java",
    "go",
    "sql",
]

# File extension to language mapping
EXTENSION_TO_LANGUAGE: dict[str, Language] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".php": "php",
    ".svelte": "svelte",
    ".cs": "csharp",
    ".dart": "dart",
    ".java": "java",
    ".go": "go",
    ".sql": "sql",
    ".sqlproj": "sql",
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
    depends_on: list[str] = Field(
        default_factory=list,
        description="Dependencies extracted from signature (e.g., constructor params)",
    )


class ScanResult(BaseModel):
    """Result of scanning a directory or file.

    Attributes:
        symbols: List of extracted symbols.
        files_scanned: Number of files processed (an extractor ran).
        files_found: Number of files that passed the exclude filter and
            reached language dispatch — the honesty counter for exit-code
            decisions (RAISE-17096). Invariant (C1): ``files_found ==
            files_scanned + len(errors) + sum(skipped_by_extension.values())``.
        skipped_by_extension: Count of found-but-unprocessed files, keyed
            by lowercase suffix (``"(no extension)"`` for none) — the data
            behind the "found N files but scanned 0" diagnostic.
        errors: List of files that failed to parse.
        diagnostics: Extractor-level notices that are not errors (e.g. the
            T-SQL preview summary, ``.sqlproj`` gate notices — RAISE-17097).
            Empty for languages with no diagnostics to report.
        unresolved_references: Normalized names referenced via
            ``Symbol.depends_on`` that did not resolve to any extracted
            symbol in this scan. Computed once at scan level over SQL
            symbols only (RAISE-17097 D-S2-7); empty for non-SQL scans.

    Examples:
        >>> result = ScanResult(symbols=[], files_scanned=5, errors=[])
        >>> result.files_scanned
        5
    """

    symbols: list[Symbol] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    files_scanned: int = Field(default=0)
    files_found: int = Field(default=0)
    skipped_by_extension: dict[str, int] = Field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    errors: list[str] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    diagnostics: list[str] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    unresolved_references: list[str] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]


class GrammarNotAvailableError(RuntimeError):
    """Raised when a tree-sitter grammar required for scanning is not installed."""


_GRAMMAR_PACKAGES: dict[str, str] = {
    "csharp": "tree-sitter-c-sharp",
    "typescript": "tree-sitter-typescript",
    "javascript": "tree-sitter-javascript",
    "php": "tree-sitter-php",
    "svelte": "tree-sitter-svelte",
    "dart": "tree-sitter-language-pack",
    "java": "tree-sitter-java",
    "go": "tree-sitter-go",
}

_GRAMMAR_MODULES: dict[str, str] = {
    "csharp": "tree_sitter_c_sharp",
    "typescript": "tree_sitter_typescript",
    "javascript": "tree_sitter_javascript",
    "php": "tree_sitter_php",
    "svelte": "tree_sitter_svelte",
    "dart": "tree_sitter_language_pack",
    "java": "tree_sitter_java",
    "go": "tree_sitter_go",
}


def _check_grammar_available(language: Language) -> None:
    """Fail fast if the tree-sitter grammar for *language* is not installed."""
    module_name = _GRAMMAR_MODULES.get(language)
    if module_name is None:
        return
    import importlib

    try:
        importlib.import_module(module_name)
    except ImportError:
        pkg = _GRAMMAR_PACKAGES[language]
        raise GrammarNotAvailableError(
            f"Grammar for {language!r} is not installed. "
            f"Install with: uv add {pkg}"
        ) from None


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


def _get_ts_parser(language: Language, *, file_path: str = "") -> Parser:
    """Get a tree-sitter parser for TypeScript or JavaScript.

    Args:
        language: Either "typescript" or "javascript".
        file_path: File path (used to dispatch .tsx to TSX parser).

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

        is_tsx = file_path.endswith(".tsx")
        if is_tsx:
            lang = TSLanguage(ts_typescript.language_tsx())
        else:
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


def _extract_doc_comment(node: Node, source: bytes) -> str | None:  # noqa: C901
    """Extract doc-comment from preceding sibling comments.

    Walks backwards through prev_sibling to collect consecutive comment nodes
    that are immediately adjacent (no blank lines). Handles patterns:
    - /// (triple-slash)
    - /** ... */ (block comment)
    - /* ... */ (block comment)
    - // (single-line)
    - # (hash, for PHP)

    Returns combined comment text with markers stripped, or None if no adjacent comments.
    """
    import re

    comments: list[str] = []
    current_node: Node | None = node.prev_sibling
    expected_end_line = node.start_point[0]

    while current_node is not None:
        if current_node.type not in ("comment", "line_comment", "block_comment"):
            break

        comment_end_line = current_node.end_point[0]
        if comment_end_line != expected_end_line - 1:
            break

        text = _get_node_text(current_node, source).strip()

        if (
            text.startswith("/**")
            and text.endswith("*/")
            or text.startswith("/*")
            and text.endswith("*/")
        ):
            lines = text.split("\n")
            cleaned = []
            for i, line in enumerate(lines):
                line = line.strip()
                if i == 0:
                    line = re.sub(r"^/\*+\s*", "", line)
                if i == len(lines) - 1:
                    line = re.sub(r"\s*\*+/$", "", line)
                if not (i == 0 and not line) and not (i == len(lines) - 1 and not line):
                    line = re.sub(r"^\*\s?", "", line)
                    if line:
                        cleaned.append(line)
            comments.insert(0, "\n".join(cleaned))
        elif text.startswith("///"):
            cleaned = re.sub(r"^///\s?", "", text)
            if cleaned:
                comments.insert(0, cleaned)
        elif text.startswith("//"):
            cleaned = re.sub(r"^//\s?", "", text)
            if cleaned:
                comments.insert(0, cleaned)
        elif text.startswith("#"):
            cleaned = re.sub(r"^#\s?", "", text)
            if cleaned:
                comments.insert(0, cleaned)

        expected_end_line = current_node.start_point[0]
        current_node = current_node.prev_sibling

    return "\n".join(comments) if comments else None


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

    if node_type in ("function_declaration", "generator_function_declaration"):
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        # Check for return type annotation
        return_type = _find_child_by_type(node, "type_annotation")
        if return_type:
            return f"function {name}{params}{_get_node_text(return_type, source)}"
        return f"function {name}{params}"

    if node_type in ("method_definition", "method_signature"):
        name_node = _find_child_by_type(node, "property_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        return f"{name}{params}"

    if node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"enum {name}"

    if node_type == "type_alias_declaration":
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"type {name}"

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
    parser = _get_ts_parser("typescript", file_path=file_path)
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


def _extract_ts_js_exported_const(
    node: Node,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
) -> None:
    """Extract exported const variable declarations as constants."""
    # export_statement → declaration → lexical_declaration → variable_declarator
    # Also handle top-level lexical_declaration directly
    decl = node
    if node.type == "export_statement":
        decl = _find_child_by_type(node, "lexical_declaration")
        if decl is None:
            return

    if decl.type != "lexical_declaration":
        return

    # Only extract 'const' (not 'let' or 'var')
    first_child = decl.children[0] if decl.children else None
    if first_child is None or _get_node_text(first_child, source) != "const":
        return

    for child in decl.children:
        if child.type == "variable_declarator":
            name_node = _find_child_by_type(child, "identifier")
            if name_node:
                name = _get_node_text(name_node, source)
                symbols.append(
                    Symbol(
                        name=name,
                        kind="constant",
                        file=file_path,
                        line=child.start_point[0] + 1,
                        signature=f"const {name}",
                    )
                )


# TS/JS node type sets (module-level constants for _walk_ts_js_node)
_TS_CLASS_TYPES = frozenset({"class_declaration"})
_TS_FUNCTION_TYPES = frozenset(
    {"function_declaration", "generator_function_declaration"}
)
_TS_METHOD_TYPES = frozenset({"method_definition", "method_signature"})
_TS_INTERFACE_TYPES = frozenset({"interface_declaration"})
_TS_ENUM_TYPES = frozenset({"enum_declaration"})
_TS_TYPE_ALIAS_TYPES = frozenset({"type_alias_declaration"})


def _walk_ts_js_node(  # noqa: C901 -- AST walker with many node types; inherent complexity
    node: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
    parent_class: str | None = None,
) -> None:
    """Walk a TS/JS tree-sitter node and collect symbols."""
    node_type = node.type

    if node_type in _TS_CLASS_TYPES:
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=name,
                kind="class",
                file=file_path,
                line=node.start_point[0] + 1,  # tree-sitter is 0-indexed
                signature=_extract_ts_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

        # Walk class body for methods
        body = _find_child_by_type(node, "class_body")
        if body:
            for child in body.children:
                _walk_ts_js_node(
                    child,
                    symbols=symbols,
                    source=source,
                    file_path=file_path,
                    parent_class=name,
                )
        return  # Don't recurse further into class

    if node_type in _TS_FUNCTION_TYPES and parent_class is None:
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=name,
                kind="function",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_ts_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

    elif node_type in _TS_METHOD_TYPES and parent_class is not None:
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
                docstring=_extract_doc_comment(node, source),
            )
        )

    elif node_type in _TS_INTERFACE_TYPES:
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=name,
                kind="interface",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_ts_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

    elif node_type in _TS_ENUM_TYPES:
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=name,
                kind="enum",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_ts_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

    elif node_type in _TS_TYPE_ALIAS_TYPES:
        name_node = _find_child_by_type(node, "type_identifier", "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=name,
                kind="type_alias",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_ts_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

    elif node_type == "export_statement":
        # Handle exported const declarations
        _extract_ts_js_exported_const(node, symbols, source, file_path)

    # Recurse into children
    for child in node.children:
        _walk_ts_js_node(
            child,
            symbols=symbols,
            source=source,
            file_path=file_path,
            parent_class=parent_class,
        )


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
    _walk_ts_js_node(root, symbols=symbols, source=source, file_path=file_path)
    return symbols


def _get_php_parser() -> Parser:
    """Get a tree-sitter parser for PHP.

    Returns:
        Configured tree-sitter Parser.

    Raises:
        ImportError: If tree-sitter-php is not installed.
    """
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for PHP scanning. "
            "Install with: uv add tree-sitter tree-sitter-php"
        ) from e

    import tree_sitter_php as ts_php

    lang = TSLanguage(ts_php.language_php())
    return Parser(lang)


def _extract_php_signature(node: Node, source: bytes) -> str:  # noqa: C901 -- complexity 14, refactor deferred
    """Extract a signature from a PHP AST node."""
    node_type = node.type

    if node_type == "class_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        parts = [f"class {name}"]
        base = _find_child_by_type(node, "base_clause")
        if base:
            parts.append(_get_node_text(base, source))
        iface = _find_child_by_type(node, "class_interface_clause")
        if iface:
            parts.append(_get_node_text(iface, source))
        return " ".join(parts)

    if node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    if node_type == "trait_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"trait {name}"

    if node_type == "function_definition":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        # Return type
        ret_type = _find_child_by_type(node, "primitive_type", "named_type")
        if ret_type:
            return f"function {name}{params}: {_get_node_text(ret_type, source)}"
        return f"function {name}{params}"

    if node_type == "method_declaration":
        parts: list[str] = []
        vis = _find_child_by_type(node, "visibility_modifier")
        if vis:
            parts.append(_get_node_text(vis, source))
        static = _find_child_by_type(node, "static_modifier")
        if static:
            parts.append("static")
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        parts.append(f"function {name}")
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        sig = " ".join(parts) + params
        ret_type = _find_child_by_type(node, "primitive_type", "named_type")
        if ret_type:
            sig += f": {_get_node_text(ret_type, source)}"
        return sig

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        # Backed enum type (e.g., ": string")
        ret_type = _find_child_by_type(node, "primitive_type")
        if ret_type:
            return f"enum {name}: {_get_node_text(ret_type, source)}"
        return f"enum {name}"

    return ""


def _qualify_php_name(ns: list[str], name: str) -> str:
    """Qualify a PHP name with its namespace.

    Uses dot separator for internal IDs — PHP uses backslash for namespaces
    but backslashes in component IDs break JSON, graph queries, and ID dedup.
    """
    return f"{ns[0]}.{name}" if ns[0] else name


# PHP container types (module-level constant for _walk_php_node)
_PHP_CONTAINER_TYPES = frozenset(
    {
        "class_declaration",
        "interface_declaration",
        "trait_declaration",
    }
)


def _walk_php_node(  # noqa: C901 -- AST walker with many PHP node types; inherent complexity
    node: Node,
    *,
    symbols: list[Symbol],
    ns: list[str],
    source: bytes,
    file_path: str,
    parent_name: str | None = None,
) -> None:
    """Walk a PHP tree-sitter node and collect symbols."""
    node_type = node.type

    if node_type == "namespace_definition":
        ns_node = _find_child_by_type(node, "namespace_name")
        if ns_node:
            # Normalize PHP backslash separators to dots for graph IDs
            ns[0] = _get_node_text(ns_node, source).replace("\\", ".")
        # Continue walking children (declarations inside namespace)
        for child in node.children:
            _walk_php_node(
                child,
                symbols=symbols,
                ns=ns,
                source=source,
                file_path=file_path,
                parent_name=parent_name,
            )
        return

    if node_type in _PHP_CONTAINER_TYPES:
        name_node = _find_child_by_type(node, "name")
        local_name = _get_node_text(name_node, source) if name_node else "unknown"
        qualified = _qualify_php_name(ns, local_name)

        kind: SymbolKind = "class"
        if node_type == "interface_declaration":
            kind = "interface"
        elif node_type == "trait_declaration":
            kind = "trait"

        symbols.append(
            Symbol(
                name=qualified,
                kind=kind,
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_php_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

        # Walk declaration_list for methods
        body = _find_child_by_type(node, "declaration_list")
        if body:
            for child in body.children:
                _walk_php_node(
                    child,
                    symbols=symbols,
                    ns=ns,
                    source=source,
                    file_path=file_path,
                    parent_name=qualified,
                )
        return

    if node_type == "method_declaration" and parent_name is not None:
        name_node = _find_child_by_type(node, "name")
        local_name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=local_name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_php_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "function_definition" and parent_name is None:
        name_node = _find_child_by_type(node, "name")
        local_name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=_qualify_php_name(ns, local_name),
                kind="function",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_php_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "name")
        local_name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=_qualify_php_name(ns, local_name),
                kind="enum",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_php_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    # Recurse into children
    for child in node.children:
        _walk_php_node(
            child,
            symbols=symbols,
            ns=ns,
            source=source,
            file_path=file_path,
            parent_name=parent_name,
        )


def _extract_php_symbols(
    root: Node,
    source: bytes,
    file_path: str,
) -> list[Symbol]:
    """Extract symbols from a PHP tree-sitter parse tree.

    Walks the AST and extracts classes, interfaces, traits, functions,
    methods, and enums. Tracks namespace for qualified names.

    Args:
        root: Root node of the tree-sitter parse tree.
        source: Source code as bytes.
        file_path: Path to the source file.

    Returns:
        List of Symbol objects.
    """
    symbols: list[Symbol] = []
    # Mutable container for namespace (modified by walker)
    ns: list[str] = [""]
    _walk_php_node(root, symbols=symbols, ns=ns, source=source, file_path=file_path)
    return symbols


def extract_php_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from PHP source code.

    Uses tree-sitter to parse PHP and extract classes, interfaces,
    traits, functions, methods, and enums.

    Args:
        source: PHP source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... <?php
        ... class User {
        ...     public function getName(): string {}
        ... }
        ... '''
        >>> symbols = extract_php_symbols(source, "User.php")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_php_parser()
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return _extract_php_symbols(tree.root_node, source_bytes, file_path)


# -----------------------------------------------------------------------------
# Svelte Extraction (tree-sitter-svelte + JS/TS re-parse)
# -----------------------------------------------------------------------------


def _get_svelte_parser() -> Parser:
    """Get a tree-sitter parser for Svelte.

    Returns:
        Configured tree-sitter Parser.

    Raises:
        ImportError: If tree-sitter-svelte is not installed.
    """
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for Svelte scanning. "
            "Install with: uv add tree-sitter tree-sitter-svelte"
        ) from e

    import tree_sitter_svelte

    lang = TSLanguage(tree_sitter_svelte.language())
    return Parser(lang)


def _detect_svelte_script_lang(script_element: Node, source: bytes) -> Language:  # noqa: C901 -- complexity 13, refactor deferred
    """Detect whether a Svelte script block uses TypeScript or JavaScript.

    Checks for ``lang="ts"`` or ``lang="typescript"`` attribute on the
    ``<script>`` tag.

    Args:
        script_element: The ``script_element`` node from tree-sitter-svelte.
        source: Source code as bytes.

    Returns:
        ``"typescript"`` if lang attribute indicates TS, else ``"javascript"``.
    """
    for child in script_element.children:
        if child.type != "start_tag":
            continue
        for attr in child.children:
            if attr.type != "attribute":
                continue
            attr_name: Node | None = None
            attr_value: Node | None = None
            for part in attr.children:
                if part.type == "attribute_name":
                    attr_name = part
                elif part.type == "quoted_attribute_value":
                    attr_value = part
            if attr_name is None or attr_value is None:
                continue
            name_text = source[attr_name.start_byte : attr_name.end_byte].decode(
                "utf-8"
            )
            if name_text != "lang":
                continue
            # Extract value from quoted_attribute_value → attribute_value
            for val_child in attr_value.children:
                if val_child.type == "attribute_value":
                    val_text = source[val_child.start_byte : val_child.end_byte].decode(
                        "utf-8"
                    )
                    if val_text in ("ts", "typescript"):
                        return "typescript"
    return "javascript"


def extract_svelte_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from Svelte source code.

    Uses a two-pass approach:
    1. Parse with tree-sitter-svelte to find ``<script>`` blocks
    2. Re-parse script content with JS or TS tree-sitter parser

    Each ``.svelte`` file is also registered as a ``"component"`` symbol.

    Args:
        source: Svelte source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... <script>
        ...   function hello() {}
        ... </script>
        ... '''
        >>> symbols = extract_svelte_symbols(source, "App.svelte")
        >>> symbols[0].kind
        'component'
    """
    source_bytes = source.encode("utf-8")
    component_name = Path(file_path).stem

    symbols: list[Symbol] = [
        Symbol(
            name=component_name,
            kind="component",
            file=file_path,
            line=1,
            signature=f"component {component_name}",
        )
    ]

    svelte_parser = _get_svelte_parser()
    svelte_tree = svelte_parser.parse(source_bytes)
    root = svelte_tree.root_node

    for script_el in root.children:
        if script_el.type != "script_element":
            continue

        # Detect lang="ts" on this specific script element
        script_lang = _detect_svelte_script_lang(script_el, source_bytes)

        # Find raw_text content
        raw_text_node: Node | None = None
        for sub in script_el.children:
            if sub.type == "raw_text":
                raw_text_node = sub
                break
        if raw_text_node is None:
            continue

        content = source_bytes[raw_text_node.start_byte : raw_text_node.end_byte]
        if not content.strip():
            continue

        # Line offset: raw_text starts on the line after <script>
        line_offset = raw_text_node.start_point[0]

        # Parse script content with JS or TS parser
        js_parser = _get_ts_parser(script_lang, file_path=file_path)
        js_tree = js_parser.parse(content)
        script_symbols = _extract_ts_js_symbols(js_tree.root_node, content, file_path)

        # Adjust line numbers by offset
        for sym in script_symbols:
            sym_with_offset = Symbol(
                name=sym.name,
                kind=sym.kind,
                file=sym.file,
                line=sym.line + line_offset,
                signature=sym.signature,
                docstring=sym.docstring,
                parent=sym.parent,
            )
            symbols.append(sym_with_offset)

    return symbols


# -----------------------------------------------------------------------------
# C# Extraction (tree-sitter-c-sharp)
# -----------------------------------------------------------------------------


def _get_csharp_parser() -> Parser:
    """Get a tree-sitter parser for C#.

    Returns:
        Configured tree-sitter Parser.

    Raises:
        ImportError: If tree-sitter-c-sharp is not installed.
    """
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for C# scanning. "
            "Install with: uv add tree-sitter tree-sitter-c-sharp"
        ) from e

    import tree_sitter_c_sharp

    lang = TSLanguage(tree_sitter_c_sharp.language())
    return Parser(lang)


def _extract_csharp_signature(node: Node, source: bytes) -> str:  # noqa: C901 -- AST signature extraction with many node types
    """Extract a signature from a C# AST node."""
    node_type = node.type

    if node_type == "class_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        base_list = _find_child_by_type(node, "base_list")
        if base_list:
            return f"class {name} {_get_node_text(base_list, source)}"
        return f"class {name}"

    if node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    if node_type == "struct_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        base_list = _find_child_by_type(node, "base_list")
        if base_list:
            return f"struct {name} {_get_node_text(base_list, source)}"
        return f"struct {name}"

    if node_type == "record_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"record {name}"

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"enum {name}"

    if node_type == "method_declaration":
        parts: list[str] = []
        for child in node.children:
            if child.type == "modifier":
                parts.append(_get_node_text(child, source))
        # Return type
        ret_type = _find_child_by_type(
            node, "predefined_type", "identifier", "generic_name", "void_keyword"
        )
        if ret_type:
            parts.append(_get_node_text(ret_type, source))
        name_node = _find_child_by_type(node, "identifier")
        if name_node:
            # Skip if this is the return type identifier we already added
            name_text = _get_node_text(name_node, source)
            # Find the method name (last identifier before parameter_list)
            method_name = name_text
            for child in node.children:
                if child.type == "identifier":
                    method_name = _get_node_text(child, source)
                elif child.type == "parameter_list":
                    break
            parts.append(method_name)
        params_node = _find_child_by_type(node, "parameter_list")
        if params_node:
            parts.append(_get_node_text(params_node, source))
        return " ".join(parts)

    if node_type == "property_declaration":
        parts_p: list[str] = []
        for child in node.children:
            if child.type == "modifier":
                parts_p.append(_get_node_text(child, source))
        ret_type = _find_child_by_type(
            node, "predefined_type", "identifier", "generic_name"
        )
        if ret_type:
            parts_p.append(_get_node_text(ret_type, source))
        name_node = _find_child_by_type(node, "identifier")
        if name_node:
            parts_p.append(_get_node_text(name_node, source))
        return " ".join(parts_p)

    return ""


def _get_csharp_name(node: Node, source: bytes) -> str:
    """Get the identifier name from a C# AST node."""
    name_node = _find_child_by_type(node, "identifier")
    return _get_node_text(name_node, source) if name_node else "unknown"


def _extract_csharp_constructor_deps(  # noqa: C901
    body: Node,
    source: bytes,
) -> list[str]:
    """Extract dependency type names from constructor parameters in a C# class body.

    Walks all constructor_declaration nodes in the body, collects parameter type
    names, and returns non-primitive custom types (interfaces, classes).

    Args:
        body: The declaration_list node of the class.
        source: Source code as bytes.

    Returns:
        Deduplicated list of dependency type names.
    """
    deps: list[str] = []
    for child in body.children:
        if child.type != "constructor_declaration":
            continue
        param_list = _find_child_by_type(child, "parameter_list")
        if not param_list:
            continue
        for param in param_list.children:
            if param.type != "parameter":
                continue
            for pchild in param.children:
                if pchild.type == "predefined_type":
                    break  # primitive — skip
                if pchild.type == "generic_name":
                    # e.g. IRepository<User> → IRepository
                    name_node = _find_child_by_type(pchild, "identifier")
                    if name_node:
                        deps.append(_get_node_text(name_node, source))
                    break
                if pchild.type == "identifier":
                    deps.append(_get_node_text(pchild, source))
                    break
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for dep in deps:
        if dep not in seen:
            seen.add(dep)
            result.append(dep)
    return result


# C# container types (module-level constant for _walk_csharp_node)
_CS_CONTAINER_TYPES = frozenset(
    {
        "class_declaration",
        "interface_declaration",
        "struct_declaration",
        "record_declaration",
    }
)


def _walk_csharp_node(  # noqa: C901 -- AST walker with many C# node types; inherent complexity
    node: Node,
    *,
    symbols: list[Symbol],
    ns: list[str],
    source: bytes,
    file_path: str,
    parent_name: str | None = None,
) -> None:
    """Walk a C# tree-sitter node and collect symbols."""
    node_type = node.type

    if node_type == "namespace_declaration":
        ns_node = _find_child_by_type(node, "qualified_name", "identifier")
        if ns_node:
            ns[0] = _get_node_text(ns_node, source)
        body = _find_child_by_type(node, "declaration_list")
        if body:
            for child in body.children:
                _walk_csharp_node(
                    child,
                    symbols=symbols,
                    ns=ns,
                    source=source,
                    file_path=file_path,
                    parent_name=parent_name,
                )
        return

    if node_type in _CS_CONTAINER_TYPES:
        local_name = _get_csharp_name(node, source)

        kind: SymbolKind = "class"
        if node_type == "interface_declaration":
            kind = "interface"

        body = _find_child_by_type(node, "declaration_list")
        deps = _extract_csharp_constructor_deps(body, source) if body else []

        symbols.append(
            Symbol(
                name=local_name,
                kind=kind,
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_csharp_signature(node, source),
                depends_on=deps,
                docstring=_extract_doc_comment(node, source),
            )
        )

        if body:
            for child in body.children:
                _walk_csharp_node(
                    child,
                    symbols=symbols,
                    ns=ns,
                    source=source,
                    file_path=file_path,
                    parent_name=local_name,
                )
        return

    if node_type == "method_declaration" and parent_name is not None:
        # Find the method name — last identifier before parameter_list
        method_name = "unknown"
        for child in node.children:
            if child.type == "identifier":
                method_name = _get_node_text(child, source)
            elif child.type == "parameter_list":
                break

        symbols.append(
            Symbol(
                name=method_name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_csharp_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "property_declaration" and parent_name is not None:
        local_name = _get_csharp_name(node, source)
        symbols.append(
            Symbol(
                name=local_name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_csharp_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "enum_declaration":
        local_name = _get_csharp_name(node, source)
        symbols.append(
            Symbol(
                name=local_name,
                kind="enum",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_csharp_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    for child in node.children:
        _walk_csharp_node(
            child,
            symbols=symbols,
            ns=ns,
            source=source,
            file_path=file_path,
            parent_name=parent_name,
        )


def _extract_csharp_symbols_from_tree(
    root: Node,
    source: bytes,
    file_path: str,
) -> list[Symbol]:
    """Extract symbols from a C# tree-sitter parse tree.

    Walks the AST and extracts classes, interfaces, structs, records,
    enums, methods, and properties. Tracks namespace for qualified names.

    Args:
        root: Root node of the tree-sitter parse tree.
        source: Source code as bytes.
        file_path: Path to the source file.

    Returns:
        List of Symbol objects.
    """
    symbols: list[Symbol] = []
    # Mutable container for namespace (modified by walker)
    ns: list[str] = [""]
    _walk_csharp_node(root, symbols=symbols, ns=ns, source=source, file_path=file_path)
    return symbols


def extract_csharp_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from C# source code.

    Uses tree-sitter to parse C# and extract classes, interfaces,
    structs, records, enums, methods, and properties.

    Args:
        source: C# source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... public class UserService {
        ...     public void Process() { }
        ... }
        ... '''
        >>> symbols = extract_csharp_symbols(source, "UserService.cs")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_csharp_parser()
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return _extract_csharp_symbols_from_tree(tree.root_node, source_bytes, file_path)


# ── Dart / Flutter ───────────────────────────────────────────────────────


def _get_dart_parser() -> Parser:
    """Create a tree-sitter parser for Dart.

    Uses tree-sitter-language-pack since no standalone tree-sitter-dart
    package exists on PyPI.

    Returns:
        Configured tree-sitter Parser for Dart.

    Raises:
        ImportError: If tree-sitter-language-pack is not installed.
    """
    try:
        from tree_sitter_language_pack import get_parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter-language-pack is required for Dart scanning. "
            "Install with: uv add tree-sitter-language-pack"
        ) from e

    return get_parser("dart")


def _extract_dart_signature(node: Node, source: bytes) -> str:
    """Extract a signature from a Dart AST node."""
    node_type = node.type

    if node_type == "class_definition":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        # Check for abstract modifier
        abstract_node = _find_child_by_type(node, "abstract")
        prefix = "abstract class" if abstract_node else "class"
        superclass = _find_child_by_type(node, "superclass")
        if superclass:
            return f"{prefix} {name} {_get_node_text(superclass, source)}"
        return f"{prefix} {name}"

    if node_type == "mixin_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"mixin {name}"

    if node_type == "extension_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        # Find the "on" type
        type_node = _find_child_by_type(node, "type_identifier")
        if type_node:
            return f"extension {name} on {_get_node_text(type_node, source)}"
        return f"extension {name}"

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"enum {name}"

    if node_type in {"function_signature", "method_signature"}:
        return _get_node_text(node, source).strip()

    return ""


def _get_dart_name(node: Node, source: bytes) -> str:
    """Get the identifier name from a Dart AST node."""
    name_node = _find_child_by_type(node, "identifier")
    return _get_node_text(name_node, source) if name_node else "unknown"


# Dart container types (module-level constant for _walk_dart_node)
_DART_CONTAINER_TYPES = frozenset(
    {
        "class_definition",
        "mixin_declaration",
        "extension_declaration",
    }
)


def _walk_dart_node(
    node: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
    parent_name: str | None = None,
) -> None:
    """Walk a Dart tree-sitter node and collect symbols."""
    node_type = node.type

    if node_type in _DART_CONTAINER_TYPES:
        local_name = _get_dart_name(node, source)

        kind: SymbolKind = "class"
        if node_type == "mixin_declaration":
            kind = "trait"

        symbols.append(
            Symbol(
                name=local_name,
                kind=kind,
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_dart_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )

        # Walk into body for methods
        body = _find_child_by_type(node, "class_body", "extension_body")
        if body:
            for child in body.children:
                _walk_dart_node(
                    child,
                    symbols=symbols,
                    source=source,
                    file_path=file_path,
                    parent_name=local_name,
                )
        return

    if node_type == "enum_declaration":
        local_name = _get_dart_name(node, source)
        symbols.append(
            Symbol(
                name=local_name,
                kind="enum",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_dart_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    # Top-level function: function_signature at program level
    if node_type == "function_signature" and parent_name is None:
        local_name = _get_dart_name(node, source)
        symbols.append(
            Symbol(
                name=local_name,
                kind="function",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_dart_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    # Method inside a container
    if node_type == "method_signature" and parent_name is not None:
        # method_signature contains function_signature or getter_signature
        inner = _find_child_by_type(node, "function_signature", "getter_signature")
        method_name = (
            _get_dart_name(inner, source) if inner else _get_dart_name(node, source)
        )

        symbols.append(
            Symbol(
                name=method_name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_dart_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    for child in node.children:
        _walk_dart_node(
            child,
            symbols=symbols,
            source=source,
            file_path=file_path,
            parent_name=parent_name,
        )


def _extract_dart_symbols_from_tree(
    root: Node,
    source: bytes,
    file_path: str,
) -> list[Symbol]:
    """Extract symbols from a Dart tree-sitter parse tree.

    Walks the AST and extracts classes, mixins, extensions, enums,
    top-level functions, and methods.

    Args:
        root: Root node of the tree-sitter parse tree.
        source: Source code as bytes.
        file_path: Path to the source file.

    Returns:
        List of Symbol objects.
    """
    symbols: list[Symbol] = []
    _walk_dart_node(root, symbols=symbols, source=source, file_path=file_path)
    return symbols


def extract_dart_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from Dart source code.

    Uses tree-sitter to parse Dart and extract classes, mixins,
    extensions, enums, top-level functions, and methods.

    Args:
        source: Dart source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... class UserService {
        ...     void process() {}
        ... }
        ... '''
        >>> symbols = extract_dart_symbols(source, "user_service.dart")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_dart_parser()
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return _extract_dart_symbols_from_tree(tree.root_node, source_bytes, file_path)


# ---------------------------------------------------------------------------
# Java
# ---------------------------------------------------------------------------


def _get_java_parser() -> Parser:
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for Java scanning. "
            "Install with: uv add tree-sitter tree-sitter-java"
        ) from e

    import tree_sitter_java  # type: ignore[import]

    lang = TSLanguage(tree_sitter_java.language())  # type: ignore[reportDeprecated]
    return Parser(lang)


def _extract_java_signature(node: Node, source: bytes) -> str:
    node_type = node.type

    if node_type == "class_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        implements = _find_child_by_type(node, "super_interfaces")
        extends = _find_child_by_type(node, "superclass")
        parts = [f"class {name}"]
        if extends:
            parts.append(_get_node_text(extends, source))
        if implements:
            parts.append(_get_node_text(implements, source))
        return " ".join(parts)

    if node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    if node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"enum {name}"

    if node_type in ("method_declaration", "constructor_declaration"):
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        return f"{name}{params}"

    return ""


def _walk_java_node(
    node: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
    parent_name: str | None = None,
) -> None:
    node_type = node.type

    if node_type in ("class_declaration", "interface_declaration", "enum_declaration"):
        name_node = _find_child_by_type(node, "identifier")
        local_name = _get_node_text(name_node, source) if name_node else "unknown"

        kind: SymbolKind
        if node_type == "interface_declaration":
            kind = "interface"
        elif node_type == "enum_declaration":
            kind = "enum"
        else:
            kind = "class"

        symbols.append(
            Symbol(
                name=local_name,
                kind=kind,
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_java_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )

        body = _find_child_by_type(node, "class_body", "interface_body", "enum_body")
        if body:
            for child in body.children:
                _walk_java_node(
                    child,
                    symbols=symbols,
                    source=source,
                    file_path=file_path,
                    parent_name=local_name,
                )
        return

    if (
        node_type in ("method_declaration", "constructor_declaration")
        and parent_name is not None
    ):
        name_node = _find_child_by_type(node, "identifier")
        method_name = _get_node_text(name_node, source) if name_node else "unknown"

        symbols.append(
            Symbol(
                name=method_name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_java_signature(node, source),
                parent=parent_name,
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    for child in node.children:
        _walk_java_node(
            child,
            symbols=symbols,
            source=source,
            file_path=file_path,
            parent_name=parent_name,
        )


def extract_java_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from Java source code.

    Args:
        source: Java source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... public class UserService {
        ...     public void process() {}
        ... }
        ... '''
        >>> symbols = extract_java_symbols(source, "UserService.java")
        >>> symbols[0].kind
        'class'
    """
    parser = _get_java_parser()
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    symbols: list[Symbol] = []
    _walk_java_node(
        tree.root_node, symbols=symbols, source=source_bytes, file_path=file_path
    )
    return symbols


# ---------------------------------------------------------------------------
# Go
# ---------------------------------------------------------------------------


def _get_go_parser() -> Parser:
    try:
        from tree_sitter import Language as TSLanguage
        from tree_sitter import Parser
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for Go scanning. "
            "Install with: uv add tree-sitter tree-sitter-go"
        ) from e

    import tree_sitter_go  # type: ignore[import]

    lang = TSLanguage(tree_sitter_go.language())  # type: ignore[reportDeprecated]
    return Parser(lang)


def _extract_go_signature(node: Node, source: bytes) -> str:
    node_type = node.type

    if node_type == "function_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "parameter_list")
        params = _get_node_text(params_node, source) if params_node else "()"
        return f"func {name}{params}"

    if node_type == "method_declaration":
        receiver = _find_child_by_type(node, "parameter_list")
        recv_text = _get_node_text(receiver, source) if receiver else "()"
        name_node = _find_child_by_type(node, "field_identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_nodes = [c for c in node.children if c.type == "parameter_list"]
        params = (
            _get_node_text(params_nodes[1], source) if len(params_nodes) > 1 else "()"
        )
        return f"func {recv_text} {name}{params}"

    if node_type == "type_spec":
        name_node = _find_child_by_type(node, "type_identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        inner = _find_child_by_type(node, "struct_type", "interface_type")
        if inner:
            return f"type {name} {inner.type.split('_')[0]}"
        return f"type {name}"

    return ""


def _go_receiver_type(node: Node, source: bytes) -> str | None:
    """Extract the receiver type name from a Go method declaration."""
    receiver = _find_child_by_type(node, "parameter_list")
    if not receiver:
        return None
    for c in receiver.children:
        if c.type == "parameter_declaration":
            type_node = _find_child_by_type(c, "pointer_type", "type_identifier")
            if type_node:
                if type_node.type == "pointer_type":
                    inner = _find_child_by_type(type_node, "type_identifier")
                    return _get_node_text(inner, source) if inner else None
                return _get_node_text(type_node, source)
    return None


def _collect_go_type_spec(
    spec: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
) -> None:
    """Extract symbols from a single Go type_spec node."""
    name_node = _find_child_by_type(spec, "type_identifier")
    name = _get_node_text(name_node, source) if name_node else "unknown"
    inner = _find_child_by_type(spec, "struct_type", "interface_type")
    kind: SymbolKind = (
        "interface" if inner and inner.type == "interface_type" else "class"
    )
    symbols.append(
        Symbol(
            name=name,
            kind=kind,
            file=file_path,
            line=spec.start_point[0] + 1,
            signature=_extract_go_signature(spec, source),
            docstring=_extract_doc_comment(spec, source),
        )
    )
    if inner and inner.type == "interface_type":
        for iface_child in inner.children:
            if iface_child.type == "method_elem":
                m_name_node = _find_child_by_type(iface_child, "field_identifier")
                if m_name_node:
                    m_name = _get_node_text(m_name_node, source)
                    symbols.append(
                        Symbol(
                            name=m_name,
                            kind="method",
                            file=file_path,
                            line=iface_child.start_point[0] + 1,
                            signature=m_name,
                            parent=name,
                            docstring=_extract_doc_comment(iface_child, source),
                        )
                    )


def _collect_go_consts(
    node: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
) -> None:
    """Extract constant symbols from a Go const_declaration node."""
    for child in node.children:
        if child.type == "const_spec":
            name_node = _find_child_by_type(child, "identifier")
            if name_node:
                name = _get_node_text(name_node, source)
                symbols.append(
                    Symbol(
                        name=name,
                        kind="constant",
                        file=file_path,
                        line=child.start_point[0] + 1,
                        signature=f"const {name}",
                        docstring=_extract_doc_comment(child, source),
                    )
                )


def _walk_go_node(
    node: Node,
    *,
    symbols: list[Symbol],
    source: bytes,
    file_path: str,
) -> None:
    node_type = node.type

    if node_type == "function_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        symbols.append(
            Symbol(
                name=name,
                kind="function",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_go_signature(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "method_declaration":
        name_node = _find_child_by_type(node, "field_identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        symbols.append(
            Symbol(
                name=name,
                kind="method",
                file=file_path,
                line=node.start_point[0] + 1,
                signature=_extract_go_signature(node, source),
                parent=_go_receiver_type(node, source),
                docstring=_extract_doc_comment(node, source),
            )
        )
        return

    if node_type == "type_declaration":
        for child in node.children:
            if child.type == "type_spec":
                _collect_go_type_spec(
                    child, symbols=symbols, source=source, file_path=file_path
                )
        return

    if node_type == "const_declaration":
        _collect_go_consts(node, symbols=symbols, source=source, file_path=file_path)
        return

    for child in node.children:
        _walk_go_node(child, symbols=symbols, source=source, file_path=file_path)


def extract_go_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract symbols from Go source code.

    Args:
        source: Go source code as string.
        file_path: Path to the source file (for metadata).

    Returns:
        List of Symbol objects.

    Examples:
        >>> source = '''
        ... package main
        ...
        ... func Hello() {}
        ... '''
        >>> symbols = extract_go_symbols(source, "main.go")
        >>> symbols[0].kind
        'function'
    """
    parser = _get_go_parser()
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    symbols: list[Symbol] = []
    _walk_go_node(
        tree.root_node, symbols=symbols, source=source_bytes, file_path=file_path
    )
    return symbols


# --- T-SQL regex-based preview extractor (RAISE-17097) ---
#
# Tolerant, non-parsing extraction: masks comments/strings, splits on GO
# batch separators, and matches object definitions and dependencies with
# regex. This is a *preview*, not a T-SQL parser — see SQL_PREVIEW_LIMITS.

_SQL_IDENT = r"(?:\[[^\]]+\]|\"[^\"]+\"|[#@A-Za-z_][\w$#@]*)"
_SQL_QUALIFIED = rf"{_SQL_IDENT}(?:\s*\.\s*{_SQL_IDENT}){{0,3}}"

_SQL_DEFINITION_RE = re.compile(
    rf"\b(?P<verb>CREATE(?:\s+OR\s+ALTER)?|ALTER)\s+"
    rf"(?P<kind>PROCEDURE|PROC|FUNCTION|VIEW|TRIGGER|TABLE|TYPE)\s+"
    rf"(?P<name>{_SQL_QUALIFIED})",
    re.IGNORECASE,
)
_SQL_DEPENDENCY_RE = re.compile(
    rf"\b(?:FROM|JOIN|INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE(?:\s+INTO)?|EXEC(?:UTE)?)\s+"
    rf"(?P<name>{_SQL_QUALIFIED})",
    re.IGNORECASE,
)
_SQL_TVP_RE = re.compile(
    rf"@[A-Za-z_]\w*\s+(?:AS\s+)?(?P<name>{_SQL_QUALIFIED})\s+READONLY\b",
    re.IGNORECASE,
)
_SQL_MASK_RE = re.compile(r"--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'", re.DOTALL)
_SQL_GO_RE = re.compile(r"^[ \t]*GO(?:[ \t]+\d+)?[ \t]*$", re.IGNORECASE | re.MULTILINE)

# Keywords the dependency regex can capture as a "name" (AFTER INSERT, UPDATE
# AS ...; WITH EXECUTE AS OWNER; UPDATE STATISTICS) plus trigger pseudo-tables.
_SQL_NOISE_NAMES: frozenset[str] = frozenset(
    {
        "as",
        "set",
        "select",
        "where",
        "on",
        "begin",
        "with",
        "statistics",
        "inserted",
        "deleted",
    }
)
_SQL_ROUTINE_KINDS: frozenset[str] = frozenset(
    {"procedure", "proc", "function", "trigger", "view"}
)
_SQL_KIND_TO_SYMBOL_KIND: dict[str, SymbolKind] = {
    "table": "class",
    "view": "class",
    "type": "class",
    "procedure": "function",
    "proc": "function",
    "function": "function",
    "trigger": "function",
}
SQLPROJ_DIAGNOSTIC = (
    "{file}: preview — .sqlproj is an MSBuild project file; "
    "counted, no symbols extracted"
)
SQL_PREVIEW_LIMITS: tuple[str, ...] = (
    "EXEC @var = proc (assigned exec) not captured",
    "INSERT without INTO not captured",
    "CTE and table aliases may appear as unresolved references",
    "dynamic SQL (EXEC sp_executesql @sql) is opaque",
    "temp tables (#t, ##t) and table variables excluded",
)


class _SqlDef(NamedTuple):
    """A single SQL object definition found within one GO batch."""

    pos: int
    kind: str
    name: str
    verb: str
    depends_on: list[str]


def _normalize_sql_name(raw: str) -> str:
    """Strip bracket/quote delimiters and empty parts from a qualified name."""
    parts = [p.strip() for p in raw.split(".")]
    cleaned: list[str] = []
    for part in parts:
        if not part:
            continue
        if (part.startswith("[") and part.endswith("]")) or (
            part.startswith('"') and part.endswith('"')
        ):
            part = part[1:-1]
        cleaned.append(part)
    return ".".join(cleaned)


def _is_persistent_sql_name(name: str) -> bool:
    """True unless the first qualifier segment is a temp table or variable."""
    if not name:
        return False
    first = name.split(".", 1)[0]
    return not first.startswith("#") and not first.startswith("@")


def _is_noise_sql_name(name: str) -> bool:
    """True if the bare (rightmost) segment is a known keyword false-positive."""
    bare = name.rsplit(".", 1)[-1]
    return bare.lower() in _SQL_NOISE_NAMES


def _mask_sql(source: str) -> str:
    """Blank out comments and string literals, preserving length and newlines.

    Offset-preserving so ``Symbol.line`` stays exact after masking.
    """

    def _blank(match: re.Match[str]) -> str:
        return "".join(c if c == "\n" else " " for c in match.group(0))

    return _SQL_MASK_RE.sub(_blank, source)


def _sql_batch_spans(masked: str) -> list[tuple[int, int]]:
    """Split *masked* source into GO-separated batch spans."""
    matches = list(_SQL_GO_RE.finditer(masked))
    if not matches:
        return [(0, len(masked))]
    spans: list[tuple[int, int]] = []
    start = 0
    for m in matches:
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(masked)))
    return spans


def _sql_definitions(masked: str, start: int, end: int) -> list[_SqlDef]:
    """Match object definitions within one batch span, applying D-S2-4."""
    defs: list[_SqlDef] = []
    for m in _SQL_DEFINITION_RE.finditer(masked, start, end):
        verb = re.sub(r"\s+", " ", m.group("verb").strip()).upper()
        raw_kind = m.group("kind").lower()
        name = _normalize_sql_name(m.group("name"))
        if not _is_persistent_sql_name(name):
            continue
        bare_verb = verb.split(" ", 1)[0]
        if bare_verb == "ALTER" and raw_kind not in _SQL_ROUTINE_KINDS:
            continue
        kind = "procedure" if raw_kind == "proc" else raw_kind
        defs.append(
            _SqlDef(pos=m.start(), kind=kind, name=name, verb=verb, depends_on=[])
        )
    return defs


def _sql_dependencies(masked: str, start: int, end: int) -> list[tuple[int, str]]:
    """Match dependency references (FROM/JOIN/DML/EXEC/TVP) within one batch."""
    deps: list[tuple[int, str]] = []
    for pattern in (_SQL_DEPENDENCY_RE, _SQL_TVP_RE):
        for m in pattern.finditer(masked, start, end):
            name = _normalize_sql_name(m.group("name"))
            if (
                not name
                or not _is_persistent_sql_name(name)
                or _is_noise_sql_name(name)
            ):
                continue
            deps.append((m.start(), name))
    return deps


def _attribute_sql_dependencies(
    defs: list[_SqlDef], deps: list[tuple[int, str]]
) -> None:
    """Attribute each dependency to the nearest preceding definition (D-S2-5).

    References with no preceding definition in the batch are orphans and are
    dropped. Self-references and per-owner duplicates are also dropped.
    Mutates ``defs`` in place, then dedups/sorts each owner's dependencies.
    """
    if defs:
        positions = [d.pos for d in defs]
        for pos, name in deps:
            idx = bisect.bisect_right(positions, pos) - 1
            if idx < 0:
                continue
            owner = defs[idx]
            if owner.name.lower() == name.lower():
                continue
            owner.depends_on.append(name)
    for d in defs:
        unique: dict[str, str] = {}
        for name in d.depends_on:
            unique.setdefault(name.lower(), name)
        d.depends_on[:] = sorted(unique.values(), key=str.lower)


def extract_sql_symbols(source: str, file_path: str) -> list[Symbol]:
    """Extract T-SQL object definitions and dependencies via regex (preview).

    Not a T-SQL parser — see ``SQL_PREVIEW_LIMITS`` for known gaps. ``.sqlproj``
    files are MSBuild project XML, not T-SQL, and are gated to an empty list
    (the diagnostic is appended by ``_process_source_file``, which owns
    ``ScanResult``).

    Args:
        source: SQL source code as string.
        file_path: Path to the source file (for metadata and the
            ``.sqlproj`` extension gate).

    Returns:
        List of Symbol objects, one per distinct (kind, name) definition
        found (case-insensitive dedup — a ``CREATE`` and a later ``ALTER``
        of the same routine merge into one Symbol with unioned deps).
    """
    if Path(file_path).suffix.lower() == ".sqlproj":
        return []

    masked = _mask_sql(source)
    all_defs: list[_SqlDef] = []
    for start, end in _sql_batch_spans(masked):
        defs = _sql_definitions(masked, start, end)
        deps = _sql_dependencies(masked, start, end)
        _attribute_sql_dependencies(defs, deps)
        all_defs.extend(defs)

    merged: dict[tuple[str, str], _SqlDef] = {}
    order: list[tuple[str, str]] = []
    for d in all_defs:
        key = (d.kind, d.name.lower())
        if key not in merged:
            merged[key] = d
            order.append(key)
        else:
            existing = merged[key]
            combined = sorted({*existing.depends_on, *d.depends_on}, key=str.lower)
            merged[key] = existing._replace(depends_on=combined)

    symbols: list[Symbol] = []
    for key in order:
        d = merged[key]
        line = masked.count("\n", 0, d.pos) + 1
        signature = f"{d.verb} {d.kind.upper()} {d.name}"
        symbols.append(
            Symbol(
                name=d.name,
                kind=_SQL_KIND_TO_SYMBOL_KIND[d.kind],
                file=file_path,
                line=line,
                signature=signature,
                parent=None,
                docstring=None,
                depends_on=d.depends_on,
            )
        )
    return symbols


class ReferenceIndex[T]:
    """Conservative name resolution shared by preview counting and edges.

    Keys are lower-cased. ``(file, qualified)`` and bare ``qualified`` use
    first-wins semantics; an unqualified (bare) name resolves only when
    exactly one candidate exists anywhere in the index (D-S2-3) — qualified
    misses never fall back to a bare match.
    """

    def __init__(self) -> None:
        self._by_file_qualified: dict[tuple[str, str], T] = {}
        self._by_qualified: dict[str, T] = {}
        self._by_bare: dict[str, list[T]] = {}

    def add(self, name: str, value: T, *, file: str | None = None) -> None:
        """Register *value* under *name*, keyed by file-scoped, qualified, and bare forms."""
        key = name.lower()
        if file is not None:
            file_key = (file, key)
            if file_key not in self._by_file_qualified:
                self._by_file_qualified[file_key] = value
        if key not in self._by_qualified:
            self._by_qualified[key] = value
        bare = key.rsplit(".", 1)[-1]
        self._by_bare.setdefault(bare, []).append(value)

    def resolve(self, dep: str, *, file: str | None = None) -> T | None:
        """Resolve *dep* by file-scoped exact, qualified exact, then unique bare match."""
        key = dep.lower()
        if file is not None:
            hit = self._by_file_qualified.get((file, key))
            if hit is not None:
                return hit
        hit = self._by_qualified.get(key)
        if hit is not None:
            return hit
        if "." not in key:
            candidates = self._by_bare.get(key, [])
            if len(candidates) == 1:
                return candidates[0]
        return None


def finalize_sql_preview(result: ScanResult) -> None:
    """Compute ``unresolved_references`` and append the preview diagnostic.

    Scan-level, SQL-only (D-S2-7): per-file unresolved counts are meaningless
    since most references cross files, and restricting to ``.sql`` symbols
    keeps C#'s interface-heavy ``depends_on`` from inflating a number labelled
    "T-SQL preview". No-op when the scan contains no SQL symbols.
    """
    sql_symbols = [s for s in result.symbols if s.file.lower().endswith(".sql")]
    if not sql_symbols:
        return

    index: ReferenceIndex[str] = ReferenceIndex()
    for s in sql_symbols:
        index.add(s.name, s.name, file=s.file)

    unresolved: set[str] = set()
    reference_count = 0
    for s in sql_symbols:
        for dep in s.depends_on:
            reference_count += 1
            if index.resolve(dep, file=s.file) is None:
                unresolved.add(dep)

    result.unresolved_references = sorted(unresolved, key=str.lower)
    result.diagnostics.append(
        f"preview: T-SQL regex extractor — {len(sql_symbols)} objects, "
        f"{reference_count} references, {len(result.unresolved_references)} unresolved; "
        f"known limits: {'; '.join(SQL_PREVIEW_LIMITS)}"
    )


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


def extract_symbols(  # noqa: C901 -- language dispatch if-chain, one branch per language
    source: str, file_path: str, language: Language
) -> list[Symbol]:
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
    if language == "typescript":
        return extract_typescript_symbols(source, file_path)
    if language == "javascript":
        return extract_javascript_symbols(source, file_path)
    if language == "php":
        return extract_php_symbols(source, file_path)
    if language == "svelte":
        return extract_svelte_symbols(source, file_path)
    if language == "csharp":
        return extract_csharp_symbols(source, file_path)
    if language == "dart":
        return extract_dart_symbols(source, file_path)
    if language == "java":
        return extract_java_symbols(source, file_path)
    if language == "go":
        return extract_go_symbols(source, file_path)
    if language == "sql":
        return extract_sql_symbols(source, file_path)
    raise ValueError(f"Unsupported language: {language}")


# Default patterns to exclude when scanning directories
DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    # Directories
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/vendor/**",
    "**/dist/**",
    "**/build/**",
    "**/.git/**",
    # C#
    "*.Designer.cs",
    "**/*.g.cs",
    "**/obj/**",
    # Dart
    "**/*.g.dart",
    "**/*.freezed.dart",
    "**/*.mocks.dart",
    # Go
    "**/*.pb.go",
    "**/*_string.go",
    # Java
    "**/generated/**",
    "**/generated-sources/**",
    # JavaScript
    "**/*.min.js",
    # PHP
    "**/*.blade.php",
    # TypeScript
    "**/*.d.ts",
]

# Language-specific default glob patterns (list to support multiple extensions)
DEFAULT_LANGUAGE_PATTERNS: dict[Language | None, list[str]] = {
    "python": ["**/*.py"],
    "typescript": ["**/*.ts", "**/*.tsx"],
    "javascript": ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"],
    "php": ["**/*.php"],
    "svelte": ["**/*.svelte"],
    "csharp": ["**/*.cs"],
    "dart": ["**/*.dart"],
    "sql": ["**/*.sql", "**/*.sqlproj"],
    None: ["**/*"],  # Auto-detect: scan all files
}


def _read_gitignore(root: Path) -> list[str]:
    """Read .gitignore from *root* and convert entries to glob patterns.

    Only handles simple .gitignore entries (directory names, file globs).
    Negation patterns (``!``) and anchored paths are ignored — they cover
    edge cases that don't affect typical exclude behaviour.
    """
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return []

    patterns: list[str] = []
    try:
        for raw_line in gitignore.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            # Skip blanks, comments, negation
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            # Strip trailing slash (directory marker)
            entry = line.rstrip("/")
            # Convert to glob: wrap bare names with **/ so they match anywhere
            if "/" not in entry:
                patterns.append(f"**/{entry}/**")
            else:
                patterns.append(f"{entry}/**")
    except OSError:
        return []
    return patterns


def _is_directory_pattern(pattern: str) -> str | None:
    """Extract directory name from patterns like ``**/node_modules/**``.

    Returns the bare directory name if the pattern represents a directory
    exclusion, or None if it's a file-level pattern.
    """
    stripped = pattern.strip("*").strip("/")
    if "/" not in stripped and pattern.endswith("/**"):
        return stripped
    return None


_VENV_DIR_NAMES = (".venv", "venv")
_VENV_BOUNDARY_CHARS = ("-", ".", "_")


def _is_venv_like(part: str, dir_name: str) -> bool:
    """Match *part* against a venv *dir_name*, tolerating renamed siblings.

    A renamed virtualenv (``.venv.old``, ``venv-backup``) still starts with
    the venv marker followed by a separator, so a bare prefix isn't enough:
    it would also match an unrelated name like ``venvironment`` (RAISE-16215).
    """
    if part == dir_name:
        return True
    return part.startswith(dir_name) and part[len(dir_name) : len(dir_name) + 1] in (
        _VENV_BOUNDARY_CHARS
    )


def _should_exclude(file_path: Path, exclude_patterns: list[str]) -> bool:
    """Check if a file should be excluded based on patterns.

    Directory patterns (``**/name/**``) are matched by checking whether
    the directory name appears anywhere in the path parts. Venv directory
    patterns additionally tolerate renamed siblings (``.venv.old``), checked
    only against ancestor directories so a file literally named ``venv.py``
    isn't mistaken for one (RAISE-16215). File patterns (``**/test_*``) use
    ``PurePath.match`` which handles ``**`` correctly for filename globbing.
    """
    parts = file_path.parts
    dir_parts = parts[:-1]
    for pattern in exclude_patterns:
        dir_name = _is_directory_pattern(pattern)
        if dir_name is not None:
            if dir_name in _VENV_DIR_NAMES:
                if any(_is_venv_like(part, dir_name) for part in dir_parts):
                    return True
            elif dir_name in parts:
                return True
        elif file_path.match(pattern):
            return True
    return False


_UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")


def _read_source(file_path: Path) -> str:
    """Decode source bytes: ``utf-8-sig`` -> NUL sniff -> ``utf-16`` fallback.

    A BOM-less UTF-16LE file decodes as "successful" UTF-8 with interleaved
    NUL bytes (ASCII bytes + 0x00), so success alone is not proof of a
    correct decode — a NUL in the decoded text routes to the UTF-16 path
    instead (RAISE-17097 D-S2-9). Endianness is picked from the BOM when
    present, defaulting to little-endian (SQL Server / Windows convention)
    otherwise. Raises ``UnicodeDecodeError`` from the final attempt if every
    codec fails.
    """
    data = file_path.read_bytes()
    try:
        text = data.decode("utf-8-sig")
        if "\x00" not in text:
            return text.replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        pass
    codec = "utf-16" if data[:2] in _UTF16_BOMS else "utf-16-le"
    return data.decode(codec).replace("\r\n", "\n").replace("\r", "\n")


_WINDOWS_MAX_PATH = 260


def _long_path_diagnostic(
    path: Path,
    rel: str,
    exc: OSError,
    *,
    is_windows: bool,
    max_path: int = _WINDOWS_MAX_PATH,
) -> str:
    """Error string for a path that could not be read or listed.

    Names Windows ``MAX_PATH`` and the remedy when the path is long enough
    for that to be the likely cause; falls back to the plain exception text
    otherwise. Pure and Windows-condition-gated so it is unit-testable from
    Linux (RAISE-17099 T5, G9): a file or directory whose own path is >= 260
    characters is the one runtime condition PyInstaller's long-path-aware
    bootloader and ``LongPathsEnabled=1`` cannot both fix unless the
    registry key is actually set, so the diagnostic must always be
    actionable rather than a bare ``[WinError 3]``.
    """
    length = len(str(path))
    if is_windows and length >= max_path:
        return (
            f"{rel}: path length {length} exceeds Windows MAX_PATH ({max_path}) — "
            "enable long paths (HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem\\"
            "LongPathsEnabled=1) or move the checkout closer to the drive root"
        )
    return f"{rel}: {exc}"


def _process_source_file(
    file_path: Path, rel_str: str, language: Language, result: ScanResult
) -> None:
    """Extract symbols from a source file and update result."""
    try:
        source = _read_source(file_path)
        symbols = extract_symbols(source, rel_str, language)
        result.symbols.extend(symbols)
        result.files_scanned += 1
        if language == "sql" and file_path.suffix.lower() == ".sqlproj":
            result.diagnostics.append(SQLPROJ_DIAGNOSTIC.format(file=rel_str))
    except SyntaxError as e:
        result.errors.append(f"{rel_str}: {e}")
    except UnicodeDecodeError:
        result.errors.append(
            f"{rel_str}: unable to decode as utf-8-sig or utf-16; re-encode as UTF-8"
        )
    except OSError as e:
        result.errors.append(
            _long_path_diagnostic(file_path, rel_str, e, is_windows=os.name == "nt")
        )
    except Exception as e:
        result.errors.append(f"{rel_str}: {e}")


def _record_unlistable_dirs(
    root: Path, result: ScanResult, exclude_patterns: list[str]
) -> None:
    """Surface directories ``os.walk``/``Path.glob`` cannot list (RAISE-17099 G9).

    CPython's globber silently swallows ``OSError`` raised by ``os.scandir``
    on an unlistable directory — a directory whose own path is >= MAX_PATH
    on a non-long-path-aware Windows process vanishes from the walk with no
    trace, and ``files_found`` would never reflect it. A supplementary
    ``os.walk`` pass with an ``onerror`` hook turns that into a visible
    ``ScanResult.errors`` entry. Each failed directory also increments
    ``files_found`` by one — it stands in for the (unknown) files inside
    that directory that could never be discovered, keeping the C1 invariant
    (``files_found == files_scanned + len(errors) +
    sum(skipped_by_extension.values())``) exact rather than merely ``>=``.
    """
    is_windows = os.name == "nt"
    excluded_dir_names: set[str] = set()
    for pat in exclude_patterns:
        name = _is_directory_pattern(pat)
        if name is not None:
            excluded_dir_names.add(name)

    def _onerror(exc: OSError) -> None:
        dir_path = Path(exc.filename) if exc.filename else root
        try:
            rel = portable_path(dir_path, root)
        except ValueError:
            rel = dir_path.as_posix()
        result.files_found += 1
        result.errors.append(
            _long_path_diagnostic(dir_path, rel, exc, is_windows=is_windows)
        )

    for _dirpath, dirnames, _filenames in os.walk(root, onerror=_onerror):
        dirnames[:] = [
            d for d in dirnames if d not in excluded_dir_names
        ]


def _normalize_exclude(pattern: str) -> str:
    """Normalize an exclude pattern so bare directory names work as globs.

    Accepts:
      - Already-globbed patterns (``**/.venv/**``) → pass through
      - Bare directory names (``.venv``, ``node_modules``) → wrap as ``**/{name}/**``
      - File patterns (``*.pyc``) → pass through

    This allows ``--exclude .venv`` to work without glob characters,
    sidestepping Windows CRT wildcard expansion that breaks quoted globs.
    """
    if "**" in pattern or "*" in pattern or "?" in pattern:
        return pattern
    # Bare name without path separators or glob chars → directory pattern
    clean = pattern.replace("\\", "/").rstrip("/")
    if "/" not in clean:
        return f"**/{clean}/**"
    return f"{clean}/**"


def scan_directory(  # noqa: C901 -- complexity 11, refactor deferred
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
        ScanResult with all extracted symbols. ``files_found`` and
        ``skipped_by_extension`` are populated during the same walk (no
        extra I/O), satisfying ``files_found == files_scanned +
        len(errors) + sum(skipped_by_extension.values())`` (RAISE-17096 C1).

    Examples:
        >>> result = scan_directory(Path("src/"))  # Auto-detect
        >>> result = scan_directory(Path("src/"), language="typescript")
    """
    if exclude_patterns is None:
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)
    else:
        exclude_patterns = [_normalize_exclude(p) for p in exclude_patterns]

    # Merge .gitignore patterns when present
    gitignore_patterns = _read_gitignore(path)
    if gitignore_patterns:
        exclude_patterns = list(exclude_patterns) + gitignore_patterns

    # Resolve glob patterns: single pattern string or language-specific defaults
    if pattern is not None:
        patterns = [pattern]
    else:
        patterns = DEFAULT_LANGUAGE_PATTERNS.get(language, ["**/*"])

    if language is not None:
        _check_grammar_available(language)

    result = ScanResult()
    root = path.resolve()

    # Surface directories the glob walk below cannot see at all (RAISE-17099
    # G9) before the per-file loop, so an unlistable directory's diagnostic
    # is never lost to a silent CPython glob skip.
    _record_unlistable_dirs(root, result, exclude_patterns)

    # Collect files from all patterns, dedup by resolved path
    seen: set[Path] = set()
    for glob_pattern in patterns:
        for file_path in path.glob(glob_pattern):
            if file_path.is_dir():
                continue

            resolved = file_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)

            if _should_exclude(file_path, exclude_patterns):
                continue

            if file_path.is_relative_to(root):
                rel_str = portable_path(file_path, root)
            else:
                rel_str = file_path.as_posix()

            file_language = language or detect_language(file_path)
            result.files_found += 1
            if file_language is None:
                ext = file_path.suffix.lower() or "(no extension)"
                result.skipped_by_extension[ext] = (
                    result.skipped_by_extension.get(ext, 0) + 1
                )
                continue

            _process_source_file(file_path, rel_str, file_language, result)

    finalize_sql_preview(result)
    return result
