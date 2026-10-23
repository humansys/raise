"""Re-export shim — all symbols now live in raise_cli.hook_bus.emitter.

RAISE-16455: hook_bus moved to T5 foundation. This shim keeps existing
importers working without changes (backward-compatibility layer).
"""

from raise_cli.hook_bus.emitter import EventEmitter, create_emitter

__all__ = ["EventEmitter", "create_emitter"]
