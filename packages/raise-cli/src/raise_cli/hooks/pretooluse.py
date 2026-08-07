"""CC PreToolUse hook — governance gate (RAISE-15129) + CWD binding (ADR-098).

Invoked as: uv run python -m raise_cli.hooks.pretooluse

Two checks run in sequence, first block wins:
1. Governance gate — blocks Edit/Write to work//packages/ when no governance
   session is active (RAISE-15129).
2. CWD binding — blocks cross-worktree writes (ADR-098 Tier 1).

Fail-open en todos los casos no resolubles (ADR-094 §6):
  - raise-cli no instalado → exit 0
  - session_id vacío → exit 0 + warning
  - excepción interna → exit 0 + warning
"""

import json
import os
import sys
from pathlib import Path


def main() -> int:  # noqa: D103
    try:
        data: dict[str, object] = json.loads(sys.stdin.read() or "{}")
        cwd = str(data.get("cwd") or os.getcwd())
        env = dict(os.environ)

        from raise_cli.governance_gate import check_governance_gate

        raw_input = data.get("tool_input")
        tool_input: dict[str, object] = raw_input if isinstance(raw_input, dict) else {}
        governance_result = check_governance_gate(
            tool_name=str(data.get("tool_name") or ""),
            tool_input=tool_input,
            env=env,
            project=Path(cwd),
        )
        if governance_result == 2:
            return 2

        from raise_cli.cwd_binding import LocalCoordinationStore, evaluate_pretooluse

        store = LocalCoordinationStore(project=Path(cwd))
        return evaluate_pretooluse(data, env, store)
    except ImportError:
        print(
            "[cwd-binding] WARNING: raise-cli not available — proceeding fail-open",
            file=sys.stderr,
        )
        return 0
    except Exception as exc:  # noqa: BLE001 — fail-open by design
        print(
            f"[cwd-binding] ERROR: internal failure — proceeding fail-open: {exc}",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
