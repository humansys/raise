"""Centralized exception hierarchy for raise-cli.

This module defines all exceptions used throughout raise-cli with:
- Consistent exit codes for scripting
- Error codes for documentation/troubleshooting
- Optional hints and details for user guidance

Exit Code Table:
    0  - Success
    1  - General error (RaiError)
    2  - Configuration error
    3  - Resource not found (kata, gate)
    4  - Artifact not found
    5  - Dependency unavailable
    6  - State corruption
    7  - Validation error
    10 - Gate failed
"""

from __future__ import annotations

from typing import Any


class RaiError(Exception):
    """Base exception for all raise-cli errors.

    All raise-cli exceptions inherit from this class, providing:
    - exit_code: Process exit code for scripting
    - error_code: Unique identifier for documentation
    - message: Human-readable error description
    - hint: Optional suggestion for resolution
    - details: Optional structured data for debugging

    Example:
        >>> raise RaiError("Something went wrong", hint="Try again")
    """

    exit_code: int = 1
    error_code: str = "E000"

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a RaiError.

        Args:
            message: Human-readable error description.
            hint: Optional suggestion for resolution.
            details: Optional structured data for debugging.
        """
        self.message = message
        self.hint = hint
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return the error message."""
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON output.

        Returns:
            Dictionary with error_code, exit_code, message, hint, and details.
        """
        return {
            "error_code": self.error_code,
            "exit_code": self.exit_code,
            "message": self.message,
            "hint": self.hint,
            "details": self.details,
        }


class ConfigurationError(RaiError):
    """Configuration-related errors.

    Raised when:
    - Config file is malformed
    - Required configuration is missing
    - Configuration values are invalid

    Exit code: 2
    """

    exit_code: int = 2
    error_code: str = "E001"


class KataNotFoundError(RaiError):
    """Kata definition not found.

    Raised when a requested kata ID does not exist in .raise/katas/.

    Exit code: 3
    """

    exit_code: int = 3
    error_code: str = "E002"


class GateNotFoundError(RaiError):
    """Gate definition not found.

    Raised when a requested gate ID does not exist in .raise/gates/.

    Exit code: 3
    """

    exit_code: int = 3
    error_code: str = "E003"


class ArtifactNotFoundError(RaiError):
    """Artifact file not found.

    Raised when a referenced artifact path does not exist.

    Exit code: 4
    """

    exit_code: int = 4
    error_code: str = "E004"


class DependencyError(RaiError):
    """External dependency not available.

    Raised when a required external tool is not installed or accessible:
    - git
    - ast-grep
    - ripgrep

    Exit code: 5
    """

    exit_code: int = 5
    error_code: str = "E005"


class StateError(RaiError):
    """State file corrupted or invalid.

    Raised when:
    - State file cannot be parsed
    - State schema validation fails
    - State version mismatch

    Exit code: 6
    """

    exit_code: int = 6
    error_code: str = "E006"


class ValidationError(RaiError):
    """Schema or artifact validation failed.

    Raised when:
    - Pydantic schema validation fails
    - Artifact content validation fails
    - Input format is invalid

    Exit code: 7
    """

    exit_code: int = 7
    error_code: str = "E007"


class GateFailedError(RaiError):
    """Gate validation did not pass.

    Raised when one or more required gate criteria fail.
    This is a "business logic" failure, not a system error.

    Exit code: 10
    """

    exit_code: int = 10
    error_code: str = "E010"


class RaiSessionNotFoundError(RaiError):
    """Session ID not provided or resolvable.

    Raised when:
    - Neither --session flag nor RAI_SESSION_ID env var is provided
    - Session ID is required but cannot be determined

    Exit code: 2 (configuration error - user must provide session context)
    """

    exit_code: int = 2
    error_code: str = "E011"


# All public exceptions
__all__ = [
    "RaiError",
    "ConfigurationError",
    "KataNotFoundError",
    "GateNotFoundError",
    "ArtifactNotFoundError",
    "DependencyError",
    "StateError",
    "ValidationError",
    "GateFailedError",
    "RaiSessionNotFoundError",
]
