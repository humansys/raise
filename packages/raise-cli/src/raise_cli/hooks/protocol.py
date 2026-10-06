"""Re-export shim — all symbols now live in raise_cli.hook_bus.protocol.

RAISE-16455: hook_bus moved to T5 foundation. This shim keeps existing
importers working without changes (backward-compatibility layer).
"""

from raise_cli.hook_bus.protocol import LifecycleHook

__all__ = ["LifecycleHook"]
