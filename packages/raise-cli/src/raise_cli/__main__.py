"""Entry point for python -m raise_cli."""

from __future__ import annotations

import os
import sys

from raise_cli.cli.main import app
from raise_cli.exceptions import RaiError


def _handle_unexpected_error(error: Exception) -> None:
    """Print unexpected exception safely — no frame locals, no traceback by default.

    Frame locals are suppressed to prevent leaking API keys and tokens that may
    be in scope when the exception occurs (RAISE-18038). Set RAI_DEBUG=1 to
    include the full traceback for debugging.
    """
    import traceback

    error_type = type(error).__name__
    print(f"Unexpected error ({error_type}): {error}", file=sys.stderr)

    if os.environ.get("RAI_DEBUG") == "1":
        traceback.print_exc()
    else:
        print("Set RAI_DEBUG=1 for full traceback.", file=sys.stderr)


def main() -> None:
    """Run the CLI application with error handling.

    Catches RaiError exceptions and displays them with proper formatting,
    then exits with the appropriate exit code. Any other unhandled exception
    is caught and displayed safely (without frame locals) to prevent leaking
    API keys and tokens to the terminal and CI logs (RAISE-18038).
    """
    if os.environ.get("RAISE_TEST_BLOCK_GRAPH_BUILD") == "1" and sys.argv[1:3] == [
        "graph",
        "build",
    ]:
        print("graph build is blocked under pytest", file=sys.stderr)
        sys.exit(86)

    try:
        app()
    except RaiError as error:
        # Import here to avoid circular imports and for lazy loading
        from raise_cli.cli.error_handler import handle_error
        from raise_cli.cli.main import get_output_format

        output_format = get_output_format()
        exit_code = handle_error(error, output_format=output_format)
        sys.exit(exit_code)
    except Exception as error:  # noqa: BLE001
        _handle_unexpected_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
