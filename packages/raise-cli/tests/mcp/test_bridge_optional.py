"""Tests for RAISE-483: mcp optional dependency guard in McpBridge.

Verifies that raise_cli.mcp.bridge can be imported and McpBridgeError
is available even when the `mcp` package is not installed. McpBridge
instantiation should raise a clear McpBridgeError when mcp is missing.
"""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


def test_bridge_module_importable_without_mcp() -> None:
    """bridge.py module should import without error even if mcp is absent."""
    # Remove mcp from sys.modules to simulate it not being installed
    saved_modules: dict[str, object] = {}
    mcp_keys = [k for k in sys.modules if k == "mcp" or k.startswith("mcp.")]
    for k in mcp_keys:
        saved_modules[k] = sys.modules.pop(k)

    # Also remove the bridge module so it re-imports
    bridge_key = "raise_cli.mcp.bridge"
    saved_bridge = sys.modules.pop(bridge_key, None)

    try:
        # Block mcp imports
        original_import = (
            __builtins__.__import__
            if hasattr(__builtins__, "__import__")
            else __import__
        )  # type: ignore[union-attr]

        def _mock_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "mcp" or name.startswith("mcp."):
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)  # type: ignore[operator]

        with patch("builtins.__import__", side_effect=_mock_import):
            # Re-import bridge — should not raise
            import importlib

            bridge_mod = importlib.import_module("raise_cli.mcp.bridge")

            # McpBridgeError must still be accessible
            assert hasattr(bridge_mod, "McpBridgeError")
            assert issubclass(bridge_mod.McpBridgeError, Exception)

            # McpBridge class must be importable
            assert hasattr(bridge_mod, "McpBridge")

            # But instantiation should fail with clear error
            with pytest.raises(bridge_mod.McpBridgeError, match="mcp.*install"):
                bridge_mod.McpBridge(server_command="test")
    finally:
        # Restore original modules
        for k, v in saved_modules.items():
            sys.modules[k] = v  # type: ignore[assignment]
        if saved_bridge is not None:
            sys.modules[bridge_key] = saved_bridge
        elif bridge_key in sys.modules:
            del sys.modules[bridge_key]
