"""RaiAgentRuntime Protocol — shared agent runtime abstraction.

Lives in raise-core so both pipeline (raise-cli) and daemon (rai-agent)
can depend on it without cross-layer coupling.

Story: S1064.4 — LLM Phase Executor (D3: extract Protocol)
Epic: E1064 — Pipeline Engine Core
Extracted to raise-core: RAISE-1430
"""

from collections.abc import Awaitable, Callable
from typing import Protocol

from raise_core.runtime.models import RunConfig, RunResult


class RaiAgentRuntime(Protocol):
    """Protocol for agent runtimes.

    Two methods only -- thin abstraction.
    Swap ClaudeRuntime for another implementation without touching
    the daemon, governance, pipeline, or trigger layers.

    Implementors MUST populate ``RunResult.output_text`` with the
    agent's text output. Pipeline consumers rely on this field to
    populate ``PhaseResult.output``. The ``send`` callback is for
    streaming and may be a no-op.
    """

    async def run(
        self,
        config: RunConfig,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Execute a prompt. Returns RunResult with session_id + metrics."""
        ...

    async def resume(
        self,
        config: RunConfig,
        session_id: str,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Resume an existing session. Returns RunResult."""
        ...
