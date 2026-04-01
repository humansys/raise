"""TypeScript-specific code analyzer using tree-sitter.

Extracts imports, exports, and component counts from TypeScript modules
by parsing source files with tree-sitter-typescript.

Architecture: S1132.0a — TypeScript Import/Export Extraction
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from raise_cli.compat import portable_path
from raise_cli.context.analyzers.models import ModuleInfo
from raise_cli.discovery.scanner import (
    _get_ts_parser,  # pyright: ignore[reportPrivateUsage]
)

if TYPE_CHECKING:
    from tree_sitter import Node

_SKIP_DIRS = frozenset({"node_modules", "__pycache__", ".git", "dist", "build"})
_TS_EXTENSIONS = frozenset({".ts", ".tsx"})
_COMPONENT_NODE_TYPES = frozenset(
    {
        "class_declaration",
        "function_declaration",
        "interface_declaration",
        "enum_declaration",
        "type_alias_declaration",
    }
)


class TypeScriptAnalyzer:
    """Analyzes TypeScript modules using tree-sitter to extract structure.

    Attributes:
        src_dir: Relative path to the source directory (e.g., 'src').
    """

    def __init__(self, src_dir: str) -> None:
        self.src_dir = src_dir

    def detect(self, project_root: Path) -> bool:
        """Check if the project is a TypeScript project.

        Args:
            project_root: Root directory of the project.

        Returns:
            True if tsconfig.json exists, or package.json exists with .ts files.
        """
        if (project_root / "tsconfig.json").exists():
            return True

        if (project_root / "package.json").exists():
            src_path = project_root / self.src_dir
            if src_path.exists():
                return any(src_path.rglob("*.ts"))

        return False

    def analyze_modules(self, project_root: Path) -> list[ModuleInfo]:
        """Extract module-level structure from all TypeScript modules.

        Top-level subdirectories under src_dir are treated as modules.
        Directories must contain at least one .ts or .tsx file.

        Args:
            project_root: Root directory of the project.

        Returns:
            List of ModuleInfo for each module directory.
        """
        src_path = project_root / self.src_dir
        if not src_path.exists():
            return []

        modules: list[ModuleInfo] = []
        for entry in sorted(src_path.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith(".") or entry.name in _SKIP_DIRS:
                continue

            # Must have at least one .ts/.tsx file
            ts_files = self._collect_ts_files(entry)
            if not ts_files:
                continue

            info = self._analyze_module(entry, ts_files, project_root)
            modules.append(info)

        return modules

    def _collect_ts_files(self, module_dir: Path) -> list[Path]:
        """Collect .ts and .tsx files, skipping .d.ts declarations."""
        files: list[Path] = []
        for f in sorted(module_dir.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix not in _TS_EXTENSIONS:
                continue
            if f.name.endswith(".d.ts"):
                continue
            files.append(f)
        return files

    def _analyze_module(
        self,
        module_dir: Path,
        ts_files: list[Path],
        project_root: Path,
    ) -> ModuleInfo:
        """Analyze a single module directory.

        Args:
            module_dir: Path to the module directory.
            ts_files: Pre-collected .ts/.tsx files (excluding .d.ts).
            project_root: Root directory of the project.

        Returns:
            ModuleInfo with extracted data.
        """
        module_name = module_dir.name
        src_path = project_root / self.src_dir

        imports: set[str] = set()
        exports: set[str] = set()
        component_count = 0

        for ts_file in ts_files:
            source = self._read_file(ts_file)
            if source is None:
                continue

            tree = self._parse_file(ts_file, source)
            if tree is None:
                continue

            file_imports = self._extract_imports(
                tree, source, ts_file, module_name, src_path
            )
            imports.update(file_imports)

            file_exports = self._extract_exports(tree, source)
            exports.update(file_exports)

            component_count += self._count_components(tree)

        try:
            source_path = portable_path(module_dir, project_root)
        except ValueError:
            source_path = str(module_dir)

        return ModuleInfo(
            name=module_name,
            language="typescript",
            source_path=source_path,
            imports=sorted(imports),
            exports=sorted(exports),
            component_count=component_count,
            entry_points=[],
        )

    def _read_file(self, ts_file: Path) -> bytes | None:
        """Read a TypeScript file as bytes for tree-sitter.

        Args:
            ts_file: Path to the .ts/.tsx file.

        Returns:
            File contents as bytes, or None on failure.
        """
        try:
            return ts_file.read_bytes()
        except (OSError, UnicodeDecodeError):
            return None

    def _parse_file(self, ts_file: Path, source: bytes) -> Node | None:
        """Parse a TypeScript file into a tree-sitter tree.

        Args:
            ts_file: Path to the file (for .tsx dispatch).
            source: File contents as bytes.

        Returns:
            Root node of the parse tree, or None on failure.
        """
        try:
            parser = _get_ts_parser("typescript", file_path=str(ts_file))
            tree = parser.parse(source)
            return tree.root_node
        except (ImportError, Exception):
            return None

    def _extract_imports(
        self,
        root: Node,
        source: bytes,
        file_path: Path,
        module_name: str,
        src_path: Path,
    ) -> set[str]:
        """Extract cross-module imports from a file.

        Resolution logic:
        1. Extract source string from import_statement
        2. Only process relative imports (./ or ../)
        3. Resolve relative path to find the target module under src/
        4. Skip self-imports

        Args:
            root: Root tree-sitter node.
            source: File contents as bytes.
            file_path: Absolute path to the file.
            module_name: Current module name (to skip self-imports).
            src_path: Absolute path to the src directory.

        Returns:
            Set of imported module names.
        """
        imports: set[str] = set()

        for child in root.children:
            if child.type != "import_statement":
                continue

            source_str = self._get_import_source(child, source)
            if source_str is None:
                continue

            # Only relative imports
            if not source_str.startswith("."):
                continue

            target_module = self._resolve_import(source_str, file_path, src_path)
            if target_module is None:
                continue
            if target_module == module_name:
                continue

            imports.add(target_module)

        return imports

    def _get_import_source(self, node: Node, source: bytes) -> str | None:
        """Extract the source string from an import_statement node.

        Looks for a child `string` node and strips quotes.

        Args:
            node: An import_statement tree-sitter node.
            source: File contents as bytes.

        Returns:
            The import source path (without quotes), or None.
        """
        for child in node.children:
            if child.type == "string":
                text = source[child.start_byte : child.end_byte].decode("utf-8")
                # Strip quotes (single, double, or backtick)
                return text.strip("'\"`")
        return None

    def _resolve_import(
        self,
        source_str: str,
        file_path: Path,
        src_path: Path,
    ) -> str | None:
        """Resolve a relative import to a module name.

        Algorithm:
        1. Resolve the relative path from the importing file's directory
        2. Make it relative to src_path
        3. The first path component is the module name

        Args:
            source_str: Relative import path (e.g., '../core/runner').
            file_path: Absolute path to the importing file.
            src_path: Absolute path to the src directory.

        Returns:
            Module name string, or None if resolution fails.
        """
        try:
            file_dir = file_path.parent
            resolved = (file_dir / source_str).resolve()
            relative = resolved.relative_to(src_path.resolve())
            parts = relative.parts
            if parts:
                return parts[0]
        except (ValueError, IndexError):
            pass
        return None

    def _extract_exports(self, root: Node, source: bytes) -> set[str]:
        """Extract exported names from a file.

        Handles:
        - export function name() {}
        - export class Name {}
        - export interface Name {}
        - export enum Name {}
        - export type Name = ...
        - export const/let/var name = ...
        - export default class Name {}
        - export { Name } from './module'  (re-exports)
        - export { Name }

        Args:
            root: Root tree-sitter node.
            source: File contents as bytes.

        Returns:
            Set of exported names.
        """
        exports: set[str] = set()

        for child in root.children:
            if child.type == "export_statement":
                self._process_export_statement(child, source, exports)

        return exports

    def _process_export_statement(
        self, node: Node, source: bytes, exports: set[str]
    ) -> None:
        """Process a single export_statement node to extract exported names.

        Args:
            node: An export_statement tree-sitter node.
            source: File contents as bytes.
            exports: Set to add exported names to (mutated).
        """
        for child in node.children:
            self._process_export_child(child, source, exports)

        self._process_default_export(node, source, exports)

    def _process_export_child(
        self, child: Node, source: bytes, exports: set[str]
    ) -> None:
        """Process a single child of an export_statement.

        Args:
            child: A child node of an export_statement.
            source: File contents as bytes.
            exports: Set to add exported names to (mutated).
        """
        # export function name() / export class Name / etc.
        if child.type in _COMPONENT_NODE_TYPES:
            name = self._get_declaration_name(child, source)
            if name:
                exports.add(name)
        # export const/let/var name = ...
        elif child.type == "lexical_declaration":
            self._extract_variable_names(child, source, exports)
        # export { Name, Other } or export { Name } from './module'
        elif child.type == "export_clause":
            self._extract_export_clause_names(child, source, exports)

    def _process_default_export(
        self, node: Node, source: bytes, exports: set[str]
    ) -> None:
        """Extract names from 'export default class/function Name' statements.

        Args:
            node: An export_statement tree-sitter node.
            source: File contents as bytes.
            exports: Set to add exported names to (mutated).
        """
        text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
        if not text.startswith("export default"):
            return
        for child in node.children:
            if child.type in ("class_declaration", "function_declaration"):
                name = self._get_declaration_name(child, source)
                if name:
                    exports.add(name)

    def _get_declaration_name(self, node: Node, source: bytes) -> str | None:
        """Get the name from a declaration node.

        Args:
            node: A declaration tree-sitter node (class, function, etc.).
            source: File contents as bytes.

        Returns:
            The declared name, or None.
        """
        for child in node.children:
            if child.type in ("identifier", "type_identifier"):
                return source[child.start_byte : child.end_byte].decode("utf-8")
        return None

    def _extract_variable_names(
        self, node: Node, source: bytes, exports: set[str]
    ) -> None:
        """Extract variable names from lexical_declaration (const/let/var).

        Args:
            node: A lexical_declaration tree-sitter node.
            source: File contents as bytes.
            exports: Set to add names to (mutated).
        """
        for child in node.children:
            if child.type == "variable_declarator":
                for sub in child.children:
                    if sub.type == "identifier":
                        name = source[sub.start_byte : sub.end_byte].decode("utf-8")
                        exports.add(name)
                        break

    def _extract_export_clause_names(
        self, node: Node, source: bytes, exports: set[str]
    ) -> None:
        """Extract names from export clause: export { A, B }.

        Args:
            node: An export_clause tree-sitter node.
            source: File contents as bytes.
            exports: Set to add names to (mutated).
        """
        for child in node.children:
            if child.type == "export_specifier":
                # Use the alias if present, otherwise the name
                name_node = None
                alias_node = None
                for sub in child.children:
                    if sub.type == "identifier":
                        if name_node is None:
                            name_node = sub
                        else:
                            alias_node = sub
                target = alias_node if alias_node else name_node
                if target:
                    exports.add(
                        source[target.start_byte : target.end_byte].decode("utf-8")
                    )

    def _count_components(self, root: Node) -> int:
        """Count top-level components: classes, functions, interfaces, enums, type aliases.

        Counts both exported and non-exported top-level declarations.

        Args:
            root: Root tree-sitter node.

        Returns:
            Count of top-level component definitions.
        """
        count = 0
        for child in root.children:
            if child.type in _COMPONENT_NODE_TYPES:
                count += 1
            elif child.type == "export_statement":
                # Count exported declarations too
                for sub in child.children:
                    if sub.type in _COMPONENT_NODE_TYPES:
                        count += 1
        return count
