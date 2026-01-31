"""Entry point for python -m raise_cli."""

from __future__ import annotations

from raise_cli.cli.main import app


def main() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
