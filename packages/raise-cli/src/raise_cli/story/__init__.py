"""DEPRECATED — renamed to ``raise_cli.work_item`` (RAISE-16462, epic RAISE-16419).

This shim re-exports the old module paths for out-of-tree callers.
Scheduled for deletion in 3.2.0 — import ``raise_cli.work_item`` instead.
"""

import warnings

warnings.warn(
    "raise_cli.story is deprecated; use raise_cli.work_item (RAISE-16462)",
    DeprecationWarning,
    stacklevel=2,
)
