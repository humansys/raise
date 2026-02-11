"""Code scanner for symbol extraction.

This module extracts classes, functions, and module-level information
from source files. Supports:
- Python (via built-in ast module)
- TypeScript/JavaScript (via tree-sitter)

Example:
    >>> from rai_cli.discovery.scanner import extract_python_symbols
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
Language = Literal["python", "typescript", "javascript", "php", "svelte"]

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

    elif node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "identifier")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"enum {name}"

    elif node_type == "type_alias_declaration":
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
    enum_types = {"enum_declaration"}
    type_alias_types = {"type_alias_declaration"}

    def _extract_exported_const(node: Node) -> None:
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

        elif node_type in enum_types:
            name_node = _find_child_by_type(node, "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="enum",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_ts_signature(node, source),
                )
            )

        elif node_type in type_alias_types:
            name_node = _find_child_by_type(node, "type_identifier", "identifier")
            name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=name,
                    kind="type_alias",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_ts_signature(node, source),
                )
            )

        elif node_type == "export_statement":
            # Handle exported const declarations
            _extract_exported_const(node)

        # Recurse into children
        for child in node.children:
            walk(child, parent_class)

    walk(root)
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


def _extract_php_signature(node: Node, source: bytes) -> str:
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

    elif node_type == "interface_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"interface {name}"

    elif node_type == "trait_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        return f"trait {name}"

    elif node_type == "function_definition":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = _find_child_by_type(node, "formal_parameters")
        params = _get_node_text(params_node, source) if params_node else "()"
        # Return type
        ret_type = _find_child_by_type(node, "primitive_type", "named_type")
        if ret_type:
            return f"function {name}{params}: {_get_node_text(ret_type, source)}"
        return f"function {name}{params}"

    elif node_type == "method_declaration":
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

    elif node_type == "enum_declaration":
        name_node = _find_child_by_type(node, "name")
        name = _get_node_text(name_node, source) if name_node else "unknown"
        # Backed enum type (e.g., ": string")
        ret_type = _find_child_by_type(node, "primitive_type")
        if ret_type:
            return f"enum {name}: {_get_node_text(ret_type, source)}"
        return f"enum {name}"

    return ""


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
    namespace = ""

    # Container types whose children include methods
    container_types = {"class_declaration", "interface_declaration", "trait_declaration"}

    def _qualify(name: str) -> str:
        return f"{namespace}\\{name}" if namespace else name

    def walk(node: Node, parent_name: str | None = None) -> None:
        nonlocal namespace
        node_type = node.type

        if node_type == "namespace_definition":
            ns_node = _find_child_by_type(node, "namespace_name")
            if ns_node:
                namespace = _get_node_text(ns_node, source)
            # Continue walking children (declarations inside namespace)
            for child in node.children:
                walk(child, parent_name)
            return

        if node_type in container_types:
            name_node = _find_child_by_type(node, "name")
            local_name = _get_node_text(name_node, source) if name_node else "unknown"
            qualified = _qualify(local_name)

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
                )
            )

            # Walk declaration_list for methods
            body = _find_child_by_type(node, "declaration_list")
            if body:
                for child in body.children:
                    walk(child, parent_name=qualified)
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
                )
            )
            return

        if node_type == "function_definition" and parent_name is None:
            name_node = _find_child_by_type(node, "name")
            local_name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=_qualify(local_name),
                    kind="function",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_php_signature(node, source),
                )
            )
            return

        if node_type == "enum_declaration":
            name_node = _find_child_by_type(node, "name")
            local_name = _get_node_text(name_node, source) if name_node else "unknown"

            symbols.append(
                Symbol(
                    name=_qualify(local_name),
                    kind="enum",
                    file=file_path,
                    line=node.start_point[0] + 1,
                    signature=_extract_php_signature(node, source),
                )
            )
            return

        # Recurse into children
        for child in node.children:
            walk(child, parent_name)

    walk(root)
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


def _detect_svelte_script_lang(
    script_element: Node, source: bytes
) -> Language:
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
            name_text = source[attr_name.start_byte : attr_name.end_byte].decode("utf-8")
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
    elif language == "php":
        return extract_php_symbols(source, file_path)
    elif language == "svelte":
        return extract_svelte_symbols(source, file_path)
    else:
        raise ValueError(f"Unsupported language: {language}")


# Default patterns to exclude when scanning directories
DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/vendor/**",
    "**/dist/**",
    "**/build/**",
    "**/.git/**",
    "**/*.blade.php",
]

# Language-specific default glob patterns (list to support multiple extensions)
DEFAULT_LANGUAGE_PATTERNS: dict[Language | None, list[str]] = {
    "python": ["**/*.py"],
    "typescript": ["**/*.ts", "**/*.tsx"],
    "javascript": ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"],
    "php": ["**/*.php"],
    "svelte": ["**/*.svelte"],
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
                patterns.append(f"**/{entry}/**")
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


def _should_exclude(file_path: Path, exclude_patterns: list[str]) -> bool:
    """Check if a file should be excluded based on patterns.

    Directory patterns (``**/name/**``) are matched by checking whether
    the directory name appears anywhere in the path parts.  File patterns
    (``**/test_*``) use ``PurePath.match`` which handles ``**`` correctly
    for filename globbing.
    """
    parts = file_path.parts
    for pattern in exclude_patterns:
        dir_name = _is_directory_pattern(pattern)
        if dir_name is not None:
            if dir_name in parts:
                return True
        else:
            if file_path.match(pattern):
                return True
    return False


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
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    # Merge .gitignore patterns when present
    gitignore_patterns = _read_gitignore(path)
    if gitignore_patterns:
        exclude_patterns = list(exclude_patterns) + gitignore_patterns

    # Resolve glob patterns: single pattern string or language-specific defaults
    if pattern is not None:
        patterns = [pattern]
    else:
        patterns = DEFAULT_LANGUAGE_PATTERNS.get(language, ["**/*"])

    result = ScanResult()
    root = path.resolve()

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

            rel_path = (
                file_path.relative_to(root)
                if file_path.is_relative_to(root)
                else file_path
            )
            rel_str = str(rel_path)

            file_language = language or detect_language(file_path)
            if file_language is None:
                continue

            _process_source_file(file_path, rel_str, file_language, result)

    return result
