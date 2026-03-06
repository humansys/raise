"""Entry point for python -m raise_cli."""

from __future__ import annotations

import sys

from raise_cli.cli.main import app
from raise_cli.exceptions import RaiError


def main() -> None:
    """Run the CLI application with error handling.

    Catches RaiError exceptions and displays them with proper formatting,
    then exits with the appropriate exit code.
    """
    try:
        app()
    except RaiError as error:
        # Import here to avoid circular imports and for lazy loading
        from raise_cli.cli.error_handler import handle_error
        from raise_cli.cli.main import get_output_format

        output_format = get_output_format()
        exit_code = handle_error(error, output_format=output_format)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
