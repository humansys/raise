"""RaiSE CLI - Reliable AI Software Engineering.

A governance framework for AI-assisted software development.
"""

from __future__ import annotations

from importlib.metadata import version as _pkg_version

from raise_cli.exceptions import (
    ArtifactNotFoundError,
    ConfigurationError,
    DependencyError,
    GateFailedError,
    GateNotFoundError,
    KataNotFoundError,
    RaiError,
    StateError,
    ValidationError,
)

__version__ = _pkg_version("raise-cli")
__author__ = "Emilio Osorio"
__license__ = "MIT"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # Exceptions
    "RaiError",
    "ConfigurationError",
    "KataNotFoundError",
    "GateNotFoundError",
    "ArtifactNotFoundError",
    "DependencyError",
    "StateError",
    "ValidationError",
    "GateFailedError",
]
