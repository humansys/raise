"""Rai daemon entry point.

Usage:
    python -m rai_agent.daemon
    python -m rai_agent.daemon --config .raise/daemon.yaml --port 9000

Design decisions:
  D1: build_daemon() factory returns DaemonComponents — testable, composable
  D2: Health endpoint added directly to FastAPI app — simple, no abstraction
  D3: parse_args() separate from main() — testable without side effects
  D4: Signal handlers for graceful shutdown — SIGTERM/SIGINT
  D5: SessionRegistry + SessionDispatcher + TelegramHandler for message path
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rai_agent.daemon.app import create_app
from rai_agent.daemon.auth import NonceStore
from rai_agent.daemon.briefing import BriefingJob, BriefingPipeline
from rai_agent.daemon.config import DaemonConfig
from rai_agent.daemon.connection import make_dispatch
from rai_agent.daemon.cron import CronTrigger
from rai_agent.daemon.dispatcher import SessionDispatcher
from rai_agent.daemon.governance import GovernanceHooks, PromptAssembler
from rai_agent.daemon.keys import load_or_generate_keys
from rai_agent.daemon.registry import SessionRegistry
from rai_agent.daemon.runtime import ClaudeRuntime
from rai_agent.daemon.session import InMemorySessionManager
from rai_agent.daemon.telegram import TelegramTrigger
from rai_agent.daemon.telegram_pipeline import TelegramHandler

if TYPE_CHECKING:
    from fastapi import FastAPI

_log = logging.getLogger(__name__)


# ─── DaemonComponents ────────────────────────────────────────────────


@dataclass
class DaemonComponents:
    """All components created by build_daemon().

    Returned as a dataclass for easy access in tests and main().
    """

    app: FastAPI
    cron_trigger: CronTrigger
    telegram_trigger: TelegramTrigger
    dispatcher: SessionDispatcher
    registry: SessionRegistry
    handler: TelegramHandler
    briefing_pipeline: BriefingPipeline | None = None


# ─── build_daemon ─────────────────────────────────────────────────────


def build_daemon(config: DaemonConfig) -> DaemonComponents:
    """Build all daemon components from configuration.

    Args:
        config: Validated DaemonConfig.

    Returns:
        DaemonComponents with all wired components.
    """
    # Governance + runtime
    governance = GovernanceHooks(
        sensitive_patterns=[],
        permission_mode="bypassPermissions",
    )
    assembler = PromptAssembler(project_root=".")
    runtime = ClaudeRuntime(
        governance=governance,
        assembler=assembler,
        cwd=".",
    )

    # Triggers
    cron_trigger = CronTrigger(db_url=config.db_url)

    # Session infrastructure (S5.5)
    db_path = config.db_url.split("///")[-1] if "///" in config.db_url else "daemon.db"
    registry = SessionRegistry(
        db_path=db_path,
        max_sessions=config.max_sessions_per_chat,
    )

    # Get bot from PTB Application directly (avoid circular dep)
    from telegram.ext import Application  # type: ignore[import-untyped]

    ptb_app: Any = Application.builder().token(config.telegram_bot_token).build()
    bot: Any = ptb_app.bot

    # Handler + dispatcher
    handler = TelegramHandler(
        runtime=runtime,
        bot=bot,
        registry=registry,
    )
    dispatcher = SessionDispatcher(handler=handler.handle)

    # TelegramTrigger (uses middleware pipeline)
    telegram_trigger = TelegramTrigger(
        bot_token=config.telegram_bot_token,
        allowed_users=set(config.allowed_user_ids),
        dispatcher=dispatcher,
        registry=registry,
        handler=handler,
    )

    # Briefing pipeline (optional, still uses EventBus)
    briefing_pipeline: BriefingPipeline | None = None
    if config.briefing_chat_id is not None:
        briefing_bot: Any = telegram_trigger.bot
        briefing_pipeline = BriefingPipeline(
            runtime=runtime,
            bot=briefing_bot,
            job_id="daily-briefing",
            chat_id=config.briefing_chat_id,
        )
        briefing_pipeline.subscribe()

    # Keys
    keys = load_or_generate_keys()

    # Session + auth
    session_manager = InMemorySessionManager()
    nonce_store = NonceStore()

    # Dispatch
    dispatch = make_dispatch(runtime)

    # FastAPI app
    app = create_app(
        session_manager=session_manager,
        nonce_store=nonce_store,
        public_key=keys.public_key,
        dispatch=dispatch,
    )

    # Health endpoint
    @app.get("/health")
    async def health() -> dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        return {
            "status": "ok",
            "triggers": {
                "telegram": "configured",
                "cron": "configured",
            },
            "ws": "listening",
            "briefing": ("enabled" if config.briefing_chat_id else "disabled"),
        }

    return DaemonComponents(
        app=app,
        cron_trigger=cron_trigger,
        telegram_trigger=telegram_trigger,
        dispatcher=dispatcher,
        registry=registry,
        handler=handler,
        briefing_pipeline=briefing_pipeline,
    )


# ─── CLI ──────────────────────────────────────────────────────────────


def parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Rai daemon — agent runtime with triggers",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    return parser.parse_args(argv)


# ─── main ─────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> None:
    """Entry point for the Rai daemon.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).
    """
    # Allow launching from inside a Claude Code session (e.g. during development).
    # The SDK refuses to nest sessions when this variable is set.
    os.environ.pop("CLAUDECODE", None)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    args = parse_args(argv)

    # Load config
    if args.config:
        config = DaemonConfig.from_yaml(Path(args.config))
    else:
        config = DaemonConfig()

    # Override host/port from CLI args
    config = config.model_copy(
        update={"host": args.host, "port": args.port},
    )

    components = build_daemon(config)

    # Graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        _log.info("Shutdown signal received")
        shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    async def _run() -> None:
        import uvicorn  # type: ignore[import-untyped]

        # Init session registry
        await components.registry.init()

        # Start triggers
        await components.cron_trigger.start()
        await components.telegram_trigger.start()

        # Register briefing cron job if configured
        if config.briefing_chat_id is not None:
            briefing_job = BriefingJob(
                chat_id=config.briefing_chat_id,
            )
            await components.cron_trigger.add_job(
                job_id="daily-briefing",
                cron_expr=config.briefing_cron,
                run_config=briefing_job.build_run_config(),
            )

        # Run uvicorn
        uv_config = uvicorn.Config(
            components.app,
            host=config.host,
            port=config.port,
            log_level="info",
        )
        server = uvicorn.Server(uv_config)

        server_task = asyncio.create_task(server.serve())
        shutdown_task = asyncio.create_task(
            shutdown_event.wait(),
        )

        await asyncio.wait(
            [server_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Shutdown
        _log.info("Shutting down...")
        if not server_task.done():
            server.should_exit = True
            await server_task

        await components.telegram_trigger.stop()
        await components.cron_trigger.stop()
        await components.dispatcher.shutdown()
        await components.registry.close()

    loop.run_until_complete(_run())


if __name__ == "__main__":
    main()
