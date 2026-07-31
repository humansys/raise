"""Python-specific code analyzer using ast module.

Extracts imports, exports, and component counts from Python modules
by parsing source files with ast.parse().

Architecture: S16.1 — Code-Aware Graph
"""

from __future__ import annotations

import ast
from pathlib import Path

from raise_cli.compat import portable_path
from raise_cli.context.analyzers.models import ModuleInfo

_INIT_PY = "__init__.py"


class PythonAnalyzer:
    """Analyzes Python modules using ast to extract structure.

    Attributes:
        src_dir: Relative path to the source directory (e.g., 'src/raise_cli').
    """

    def __init__(self, src_dir: str) -> None:
        self.src_dir = src_dir
        self._package_name = Path(src_dir).name

    def detect(self, project_root: Path) -> bool:
        """Check if the project is a Python project.

        Args:
            project_root: Root directory of the project.

        Returns:
            True if pyproject.toml or setup.py exists.
        """
        return (project_root / "pyproject.toml").exists() or (
            project_root / "setup.py"
        ).exists()

    def analyze_modules(self, project_root: Path) -> list[ModuleInfo]:
        """Extract module-level structure from all Python modules.

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
            if entry.name.startswith("__"):
                continue
            if not (entry / _INIT_PY).exists():
                continue

            info = self._analyze_module(entry, project_root)
            modules.append(info)

        return modules

    def _analyze_module(self, module_dir: Path, project_root: Path) -> ModuleInfo:
        """Analyze a single module directory.

        Args:
            module_dir: Path to the module directory.
            project_root: Root directory of the project.

        Returns:
            ModuleInfo with extracted data.
        """
        module_name = module_dir.name
        py_files = sorted(module_dir.rglob("*.py"))

        imports: set[str] = set()
        component_count = 0

        for py_file in py_files:
            tree = self._parse_file(py_file)
            if tree is None:
                continue

            file_imports = self._extract_imports(tree, module_name)
            imports.update(file_imports)

            component_count += self._count_components(tree)

        exports = self._extract_exports(module_dir)

        try:
            source_path = portable_path(module_dir, project_root)
        except ValueError:
            source_path = str(module_dir)

        return ModuleInfo(
            name=module_name,
            language="python",
            source_path=source_path,
            imports=sorted(imports),
            exports=sorted(exports),
            component_count=component_count,
            entry_points=[],
        )

    def _parse_file(self, py_file: Path) -> ast.Module | None:
        """Parse a Python file into AST.

        Args:
            py_file: Path to the .py file.

        Returns:
            Parsed AST or None on failure.
        """
        try:
            source = py_file.read_text(encoding="utf-8")
            return ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            return None

    def _extract_imports(self, tree: ast.Module, module_name: str) -> set[str]:
        """Extract internal module imports, skipping TYPE_CHECKING blocks.

        Args:
            tree: Parsed AST.
            module_name: Name of the current module (to exclude self-imports).

        Returns:
            Set of imported module names (siblings only).
        """
        visitor = _ImportVisitor(self._package_name, module_name)
        visitor.visit(tree)
        return visitor.imports

    def _extract_exports(self, module_dir: Path) -> list[str]:  # noqa: C901 -- complexity 11, refactor deferred
        """Extract public API from __init__.py.

        Uses __all__ if present, otherwise imported names.

        Args:
            module_dir: Path to the module directory.

        Returns:
            List of exported names.
        """
        init_file = module_dir / _INIT_PY
        if not init_file.exists():
            return []

        tree = self._parse_file(init_file)
        if tree is None:
            return []

        # Check for __all__
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        return self._extract_all_list(node.value)

        # Fallback: extract imported names from __init__.py
        names: list[str] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom) and node.names:
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if not name.startswith("_"):
                        names.append(name)
        return names

    def _extract_all_list(self, node: ast.expr) -> list[str]:
        """Extract string values from an __all__ assignment.

        Args:
            node: The value node of the __all__ assignment.

        Returns:
            List of names from __all__.
        """
        names: list[str] = []
        if isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    names.append(elt.value)
        return names

    def _count_components(self, tree: ast.Module) -> int:
        """Count top-level classes and functions in a module.

        Args:
            tree: Parsed AST.

        Returns:
            Count of top-level class and function definitions.
        """
        count = 0
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                count += 1
        return count


class _ImportVisitor(ast.NodeVisitor):
    """AST visitor that extracts imports while skipping TYPE_CHECKING blocks.

    Attributes:
        package_name: Top-level package name (e.g., 'raise_cli').
        module_name: Current module name (to exclude self-imports).
        imports: Set of discovered sibling module names.
    """

    def __init__(self, package_name: str, module_name: str) -> None:
        self.package_name = package_name
        self.module_name = module_name
        self.imports: set[str] = set()
        self._in_type_checking = False

    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        """Skip imports inside TYPE_CHECKING blocks."""
        if self._is_type_checking(node.test):
            # Don't visit the body — skip TYPE_CHECKING imports
            for child in node.orelse:
                self.visit(child)
        else:
            self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        """Extract module name from 'from X import Y' statements."""
        if self._in_type_checking:
            return

        if node.module and node.level == 0:
            # Absolute import: from pkg.sibling.foo import bar
            self._resolve_absolute(node.module)
        elif node.level > 0 and node.module:
            # Relative import: from ..sibling import bar
            self._resolve_relative(node.module, node.level)
        elif node.level > 0 and node.names:
            # Relative import without module: from .. import sibling
            for alias in node.names:
                if node.level >= 2:
                    # from ..sibling means the name IS the sibling module
                    imported = alias.name
                    if imported != self.module_name:
                        self.imports.add(imported)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        """Extract module name from 'import X' statements."""
        if self._in_type_checking:
            return

        for alias in node.names:
            self._resolve_absolute(alias.name)

    def _resolve_absolute(self, module_path: str) -> None:
        """Resolve an absolute import to a sibling module name."""
        parts = module_path.split(".")
        # Must start with our package name
        if parts[0] != self.package_name:
            return
        if len(parts) < 2:
            return
        sibling = parts[1]
        if sibling != self.module_name:
            self.imports.add(sibling)

    def _resolve_relative(self, module_path: str, level: int) -> None:
        """Resolve a relative import to a sibling module name."""
        if level >= 2:
            # from ..sibling.foo import bar → sibling is the module
            parts = module_path.split(".")
            sibling = parts[0]
            if sibling != self.module_name:
                self.imports.add(sibling)

    def _is_type_checking(self, test: ast.expr) -> bool:
        """Check if an if-test is TYPE_CHECKING."""
        return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
            isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
        )
