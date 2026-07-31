"""DistillationHook — post-session JSONL distillation via LifecycleHook.

Subscribes to ``session:close`` and triggers the distillation pipeline
(parse → classify → persist patterns → write journal) automatically.

Architecture: ADR-039 (LifecycleHook Protocol)

Timeout note: LLM classification (DeepSeek fallback) takes 5–10 min for large sessions.
The hook spawns distillation as a detached background subprocess so it never blocks
session close and never hits the hook timeout. Fire-and-forget; errors go to logs only.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from typing import ClassVar

from raise_cli.config.paths import resolve_checkout_root
from raise_cli.hooks.events import HookEvent, HookResult, SessionCloseEvent
from raise_cli.telemetry.session_tokens import find_current_session_jsonl

logger = logging.getLogger(__name__)


class DistillationHook:
    """Distill session JSONL after every session close — best-effort, never raises.

    Subscribes to ``session:close``, finds the most recent JSONL for the current
    project via ``find_current_session_jsonl``, and spawns the full distillation
    pipeline (parse → classify → persist patterns → write journal) as a detached
    background subprocess.

    Hook failures are caught and logged — the session close is never blocked.
    """

    events: ClassVar[list[str]] = ["session:close"]
    priority: ClassVar[int] = -20
    timeout: ClassVar[float] = 10.0  # only covers subprocess spawn, not distillation

    def handle(self, event: HookEvent) -> HookResult:
        """Spawn distillation pipeline as background subprocess after session close."""
        if not isinstance(event, SessionCloseEvent):
            return HookResult(status="ok")

        root = resolve_checkout_root()
        if not (root / ".raise").is_dir():
            return HookResult(status="ok", message="No RaiSE project — skipped")

        jsonl_path = find_current_session_jsonl(root)
        if jsonl_path is None:
            logger.debug("DistillationHook: no JSONL found for %s", root)
            return HookResult(status="ok")

        try:
            # Spawn detached so LLM classification (5–10 min) never blocks session close
            subprocess.Popen(  # noqa: S603
                [
                    sys.executable,
                    "-m",
                    "raise_cli.distillation.agent",
                    "--session",
                    str(jsonl_path),
                ],
                start_new_session=True,
            )
        except Exception:  # noqa: BLE001
            logger.warning(
                "DistillationHook: failed to spawn subprocess", exc_info=True
            )
            return HookResult(
                status="ok", message="distillation spawn failed — see logs"
            )

        return HookResult(
            status="ok", message=f"Distillation started for {jsonl_path.name}"
        )
