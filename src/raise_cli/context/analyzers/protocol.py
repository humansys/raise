"""Protocol definition for code analyzers.

Architecture: S16.1 — Code-Aware Graph
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from raise_cli.context.analyzers.models import ModuleInfo


@runtime_checkable
class CodeAnalyzer(Protocol):
    """Contract for language-specific code analyzers.

    Implementations must provide:
    - detect(): Check if the project uses this language.
    - analyze_modules(): Extract module-level structure.
    """

    def detect(self, project_root: Path) -> bool:
        """Check if this analyzer applies to the given project.

        Args:
            project_root: Root directory of the project.

        Returns:
            True if the project uses this language.
        """
        ...

    def analyze_modules(self, project_root: Path) -> list[ModuleInfo]:
        """Extract module-level structure from source code.

        Args:
            project_root: Root directory of the project.

        Returns:
            List of ModuleInfo for each detected module.
        """
        ...
