"""rai-agent: Personal agent instance on RaiSE infrastructure."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("rai-agent")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
