"""Code analyzers for extracting module structure from source code.

This package provides language-specific analyzers that extract imports,
exports, and component counts from source modules. Results enrich the
unified graph with real code data alongside manually-maintained frontmatter.

Architecture: S16.1 — Code-Aware Graph
"""

from __future__ import annotations

from raise_cli.context.analyzers.models import ModuleInfo
from raise_cli.context.analyzers.protocol import CodeAnalyzer
from raise_cli.context.analyzers.python import PythonAnalyzer

__all__ = ["CodeAnalyzer", "ModuleInfo", "PythonAnalyzer"]
