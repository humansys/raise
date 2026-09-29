"""CC PostToolUse hook — MCP server staleness warning on git merge.

Invoked as: uv run python -m raise_cli.hooks.posttooluse

After a git merge/pull/rebase that modifies MCP server source files,
prints a warning advising the developer to run /mcp to reconnect.

Fail-open on all error paths (exit 0 always):
  - raise-cli not installed -> exit 0
  - JSON parse error -> exit 0
  - internal exception -> exit 0 + warning

Architecture: S8371.4 (E8371 Control-Plane Resilience)
"""

from __future__ import annotations

import json
import sys


def main() -> int:  # noqa: D103
    try:
        data: dict[str, object] = json.loads(sys.stdin.read() or "{}")

        from raise_cli.hooks.post_merge_staleness import evaluate_post_tool_use

        result = evaluate_post_tool_use(data)

        if result.warning:
            print(result.warning)

        return 0
    except ImportError:
        # raise-cli not available — no-op.
        return 0
    except Exception as exc:  # noqa: BLE001 — fail-open by design
        print(
            f"[mcp-staleness] ERROR: internal failure — proceeding fail-open: {exc}",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
