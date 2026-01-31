"""RaiSE CLI - Reliable AI Software Engineering.

A governance framework for AI-assisted software development.
"""

from __future__ import annotations

from raise_cli.exceptions import (
    ArtifactNotFoundError,
    ConfigurationError,
    DependencyError,
    GateFailedError,
    GateNotFoundError,
    KataNotFoundError,
    RaiseError,
    StateError,
    ValidationError,
)

__version__ = "2.0.0-alpha.1"
__author__ = "Emilio Osorio"
__license__ = "MIT"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # Exceptions
    "RaiseError",
    "ConfigurationError",
    "KataNotFoundError",
    "GateNotFoundError",
    "ArtifactNotFoundError",
    "DependencyError",
    "StateError",
    "ValidationError",
    "GateFailedError",
]
