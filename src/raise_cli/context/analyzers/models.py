"""Pydantic models for code analysis results.

Architecture: S16.1 — Code-Aware Graph
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModuleInfo(BaseModel):
    """Language-agnostic module analysis result.

    Attributes:
        name: Module name (e.g., 'memory', 'config').
        language: Programming language (e.g., 'python').
        source_path: Relative path to the module directory.
        imports: Other modules this one imports from.
        exports: Public API names exported by this module.
        component_count: Number of classes + top-level functions.
        entry_points: CLI commands or other entry points, if detectable.
    """

    name: str = Field(..., description="Module name")
    language: str = Field(..., description="Programming language")
    source_path: str = Field(..., description="Relative path to module directory")
    imports: list[str] = Field(
        default_factory=lambda: list[str](), description="Imported module names"
    )
    exports: list[str] = Field(
        default_factory=lambda: list[str](), description="Exported public API names"
    )
    component_count: int = Field(..., description="Classes + top-level functions")
    entry_points: list[str] = Field(
        default_factory=lambda: list[str](), description="CLI commands or entry points"
    )
