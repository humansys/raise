"""Package-level conftest for raise-cli.

Registers the opt-in profiling plugin (RAISE-14874).
The plugin is active ONLY when ``--profile-baseline`` is passed on the
command line; it is completely transparent otherwise.
"""

from __future__ import annotations

from raise_cli.testing.profiling_plugin import (
    pytest_addoption as pytest_addoption,
)
from raise_cli.testing.profiling_plugin import (
    pytest_configure as pytest_configure,
)
