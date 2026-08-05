"""Phase executor protocol and implementations.

DeterministicExecutor: S1064.3 — shell commands
LlmExecutor: S1064.4 — LLM phases via RaiAgentRuntime Protocol

Epic: E1064 — Pipeline Engine Core

Design decision D7: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import asyncio
import logging
import os
import shlex
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

from raise_cli.pipeline.prompt import resolve_prompt
from raise_core.runtime import RaiAgentRuntime, RunConfig
from raise_core.workflow.models import (
    ExecutionConfig,
    PhaseDefinition,
    PhaseResult,
    PipelineRun,
    TerminationReason,
)

logger = logging.getLogger(__name__)


def _resolve_argv(tokens: list[str]) -> list[str]:
    """Resolve the executable via ``shutil.which`` for Windows PATHEXT compat."""
    if not tokens:
        return tokens
    exe = shutil.which(tokens[0])
    if exe is not None:
        return [exe, *tokens[1:]]
    return tokens


@runtime_checkable
class PhaseExecutor(Protocol):
    """Protocol for executing a single pipeline phase."""

    async def execute(
        self,
        phase: PhaseDefinition,
        run: PipelineRun,
        config: ExecutionConfig,
    ) -> PhaseResult:
        """Execute a phase and return the result."""
        ...


class DeterministicExecutor:
    """Executes deterministic phases by running shell commands sequentially.

    Each command runs via ``asyncio.create_subprocess_exec``. Stdout and stderr
    are captured and aggregated. First non-zero exit code stops execution.

    Args:
        default_timeout: Per-command timeout in seconds. Defaults to 300.
    """

    _DEFAULT_TIMEOUT: float = 300.0

    def __init__(self, default_timeout: float | None = None) -> None:
        self._timeout = (
            default_timeout if default_timeout is not None else self._DEFAULT_TIMEOUT
        )

    async def execute(
        self,
        phase: PhaseDefinition,
        run: PipelineRun,
        config: ExecutionConfig,
    ) -> PhaseResult:
        """Run phase commands sequentially, stopping on first failure.

        Commands are trusted input from local filesystem pipeline YAML.
        The loader's 3-tier resolution (built-in → project → user) determines
        which file provides the commands.
        """
        output_parts: list[str] = []
        success = True
        termination_reason = TerminationReason.COMPLETED

        for cmd in phase.commands:
            argv = _resolve_argv(shlex.split(cmd))
            proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self._timeout,
                )
            except TimeoutError:
                proc.kill()
                await proc.wait()
                output_parts.append(f"Timeout after {self._timeout}s: {cmd}")
                success = False
                termination_reason = TerminationReason.ERROR
                break
            except BaseException:
                proc.kill()
                await proc.wait()
                raise
            if stdout:
                output_parts.append(stdout.decode())
            if stderr:
                output_parts.append(stderr.decode())
            if proc.returncode != 0:
                success = False
                termination_reason = TerminationReason.ERROR
                break

        return PhaseResult(
            success=success,
            output="".join(output_parts),
            termination_reason=termination_reason,
        )


# ─── Noop send callback (AR Q3) ─────────────────────────────────────────────


async def _noop_send(_msg: str) -> None:
    """No-op send callback for non-streaming consumers."""


# ─── Stop reason mapping ────────────────────────────────────────────────────

_STOP_REASON_MAP: dict[str, TerminationReason] = {
    "budget_exceeded": TerminationReason.BUDGET_EXCEEDED,
    "max_turns": TerminationReason.TURNS_EXCEEDED,
}


class LlmExecutor:
    """Executes LLM phases via a RaiAgentRuntime implementation.

    Constructor injection of the runtime Protocol enables swapping
    Claude for any other agent without touching this class (D1, D2).

    No ``claude_agent_sdk`` imports — all SDK coupling stays in the
    runtime implementation (e.g. ClaudeRuntime).

    Args:
        runtime: Any implementation of RaiAgentRuntime Protocol.
        skill_base: Base directory for skill SKILL.md files.
            Required when phases use ``skill`` references.
    """

    def __init__(
        self,
        runtime: RaiAgentRuntime,
        skill_base: Path | None = None,
    ) -> None:
        self._runtime = runtime
        self._skill_base = skill_base

    async def execute(
        self,
        phase: PhaseDefinition,
        run: PipelineRun,
        config: ExecutionConfig,
    ) -> PhaseResult:
        """Execute an LLM phase and return a structured result.

        Translates PhaseDefinition → RunConfig, calls runtime.run(),
        and maps RunResult → PhaseResult. Errors are caught and
        returned as PhaseResult(success=False) — never raised.
        """
        try:
            prompt = resolve_prompt(
                phase, skill_base=self._skill_base, pipeline_run=run
            )
        except (ValueError, FileNotFoundError) as exc:
            return PhaseResult(
                success=False,
                output=str(exc),
                termination_reason=TerminationReason.ERROR,
            )

        run_config = RunConfig(
            prompt=prompt,
            max_turns=phase.max_turns,
            max_budget_usd=phase.max_budget_usd,
            model=phase.model,
            permission_mode="bypassPermissions",
            cwd=str(run.worktree_path) if run.worktree_path else None,
        )

        try:
            result = await self._runtime.run(run_config, _noop_send)
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("LLM executor error: %s", exc)
            return PhaseResult(
                success=False,
                output=str(exc),
                termination_reason=TerminationReason.ERROR,
            )

        # Map SDK stop reason to TerminationReason (AR Q4)
        termination = _STOP_REASON_MAP.get(
            result.stop_reason or "", TerminationReason.COMPLETED
        )
        success = termination == TerminationReason.COMPLETED

        return PhaseResult(
            success=success,
            output=result.output_text,
            tokens_used=result.output_tokens,
            cost_usd=result.cost_usd,
            termination_reason=termination,
        )


class RoutingExecutor:
    """Dispatches phases to the appropriate executor by type.

    AR R1: PipelineEngine takes a single PhaseExecutor. This thin
    compositor routes ``phase.type`` to the correct implementation.

    Args:
        executors: Mapping of phase type to executor instance.
    """

    def __init__(self, executors: dict[str, PhaseExecutor]) -> None:
        self._executors = executors

    async def execute(
        self,
        phase: PhaseDefinition,
        run: PipelineRun,
        config: ExecutionConfig,
    ) -> PhaseResult:
        """Route to the executor matching ``phase.type``."""
        executor = self._executors.get(phase.type)
        if executor is None:
            return PhaseResult(
                success=False,
                output=f"No executor registered for phase type '{phase.type}'",
                termination_reason=TerminationReason.ERROR,
            )
        return await executor.execute(phase, run, config)


# ─── ContainerExecutor ───────────────────────────────────────────────────────


async def _materialize_snapshot(worktree_path: Path) -> Path:
    """Materializa una copia fresca del worktree vía ``git archive HEAD`` en un tempdir.

    Mecanismo de aislamiento (ADR-122 Sub-enmienda 2026-06-26, Opción 2):
    sólo incluye archivos commiteados → reproducibilidad por diseño.
    Los cambios sin commitear no se incluyen: la verificación opera sobre
    el estado registrado, no sobre el trabajo en progreso.

    Usa dos subprocesos async encadenados (sin bloquear el event loop):
    ``git archive --format=tar HEAD`` → ``tar -x -C <snapshot_dir>``.

    Returns:
        Path al tempdir creado. El caller ES responsable de limpiarlo con
        ``shutil.rmtree(path, ignore_errors=True)``.

    Raises:
        RuntimeError: Si ``git archive`` o ``tar`` fallan (repo no inicializado,
            HEAD sin commits, etc.).
    """
    snapshot_dir = Path(tempfile.mkdtemp(prefix="raise-runner-snapshot-"))
    try:
        git_proc = await asyncio.create_subprocess_exec(
            "git",
            "archive",
            "--format=tar",
            "HEAD",
            cwd=str(worktree_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        tar_data, git_err = await git_proc.communicate()
        if git_proc.returncode != 0:
            raise RuntimeError(
                f"git archive falló (exit {git_proc.returncode}): "
                f"{git_err.decode(errors='replace')}"
            )

        tar_proc = await asyncio.create_subprocess_exec(
            "tar",
            "-x",
            "-C",
            str(snapshot_dir),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, tar_err = await tar_proc.communicate(input=tar_data)
        if tar_proc.returncode != 0:
            raise RuntimeError(
                f"tar falló (exit {tar_proc.returncode}): "
                f"{tar_err.decode(errors='replace')}"
            )

        return snapshot_dir
    except Exception:
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        raise


def _build_docker_args(
    cmd: str,
    run: PipelineRun,
    image: str,
    snapshot_path: Path | None,
    container_name: str,
) -> list[str]:
    """Construye los args para ``docker run --rm`` de un solo comando (Opción 2 — snapshot).

    Cambios respecto al diseño original de bind-mount:
    - ``-v <snapshot_path>:/work`` en vez de ``-v <worktree>:/work``:
      el worktree vivo NUNCA se monta → no hay write-back, no hay archivos
      root-owned en el host (AR-1 fix).
    - ``--user <uid>:<gid>``: el container corre como el usuario del host →
      archivos escritos en el snapshot pertenecen al uid correcto → cleanup
      con ``shutil.rmtree`` funciona sin sudo (AR-1 fix).
    - ``--name <container_name>``: nombre determinístico → ``docker kill``
      puede targetear el container exacto en timeout (AR-2 fix).
    - ``--label raise-run-id=<run_id>``: el reaper de S2 (RAISE-10848) puede
      correlacionar y targetear containers por run (AR-4 fix).

    Args:
        cmd: Comando shell a ejecutar dentro del container.
        run: Estado del pipeline run (provee ``run_id`` para labels/nombre).
        image: Imagen Docker a usar.
        snapshot_path: Path al tempdir con el snapshot del worktree, o ``None``
            si ``run.worktree_path`` era ``None``.
        container_name: Nombre único para el container (formato:
            ``raise-runner-<run_id>-<i>-<uuid8>``).

    Returns:
        Lista de argumentos para ``asyncio.create_subprocess_exec``.
    """
    uid = getattr(os, "getuid", lambda: 0)()
    gid = getattr(os, "getgid", lambda: 0)()
    args: list[str] = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "--label",
        "raise-runner=1",
        "--label",
        f"raise-run-id={run.run_id}",
        "--user",
        f"{uid}:{gid}",
    ]
    if snapshot_path is not None:
        args.extend(["-v", f"{snapshot_path}:/work", "-w", "/work"])
    args.extend([image, "sh", "-c", cmd])
    return args


class _CmdOutcome:
    """Resultado de un solo comando de container. Uso interno de ContainerExecutor."""

    __slots__ = ("output_parts", "success", "early_exit")

    def __init__(
        self,
        output_parts: list[str],
        success: bool,
        early_exit: PhaseResult | None = None,
    ) -> None:
        self.output_parts = output_parts
        self.success = success
        self.early_exit = early_exit


class ContainerExecutor:
    """Ejecuta phase.commands en containers efímeros sobre snapshot del worktree (Opción 2).

    Mecanismo de aislamiento (ADR-122 Enmienda + Sub-enmienda 2026-06-26):
    por cada ``execute()`` call, materializa un snapshot fresco del worktree vía
    ``git archive HEAD`` en un tempdir, monta SOLO el snapshot (``-v <snapshot>:/work``),
    y corre el container con ``--user <uid>:<gid>``.

    El worktree vivo del host NUNCA se monta → no hay write-back,
    no hay archivos root-owned, no hay EACCES native↔container.
    El tempdir se limpia al terminar (incluso en error/timeout).

    Principio: **"la verificación no muta lo que verifica."** (ADR-122 Sub-enmienda)

    Container nombrado (``raise-runner-<run_id>-<i>-<uuid8>``) → ``docker kill``
    determinístico en timeout (AR-2). Labels ``raise-runner=1`` y
    ``raise-run-id=<run_id>`` para reaper de S2 (RAISE-10848, AR-4).

    IMPORTANTE — Semántica de verificación (wiring de S4, RAISE-10848):
        ``git archive HEAD`` captura SOLO lo commiteado en el worktree en el momento
        del ``execute()`` call. Cambios sin commitear — incluido el output típico de
        una fase ``implement`` — NO se incluyen en el snapshot.
        Diferencia intencional vs ``DeterministicExecutor``, que verifica el árbol
        vivo (D6: "la verificación opera sobre el estado registrado, no sobre el
        trabajo en progreso"). Al cablear fases en S4, las fases Container que
        verifican output de fases previas deben correr DESPUÉS de un commit explícito;
        de lo contrario verifican estado stale (HEAD anterior al trabajo).

    Args:
        image: Imagen Docker (default: ``alpine:latest``).
        default_timeout: Timeout por comando en segundos (default: 300).
    """

    _DEFAULT_IMAGE: str = "alpine:latest"
    _DEFAULT_TIMEOUT: float = 300.0

    def __init__(
        self,
        image: str | None = None,
        default_timeout: float | None = None,
    ) -> None:
        self._image = image if image is not None else self._DEFAULT_IMAGE
        self._timeout = (
            default_timeout if default_timeout is not None else self._DEFAULT_TIMEOUT
        )

    async def execute(
        self,
        phase: PhaseDefinition,
        run: PipelineRun,
        config: ExecutionConfig,
    ) -> PhaseResult:
        """Ejecuta phase.commands secuencialmente sobre snapshot fresco del worktree.

        Flujo:
        1. Materializa snapshot vía ``git archive HEAD`` en tempdir (si hay worktree y comandos).
        2. Por cada comando: ``_run_one`` corre ``docker run --rm --user --name`` sobre el snapshot.
        3. Limpia el tempdir en ``finally`` (garantizado incluso en error/timeout).

        Primer exit != 0 o timeout detiene la ejecución (stop-on-first-failure).
        Errores de docker se capturan → ``PhaseResult(success=False)`` — nunca se propagan.
        """
        all_output: list[str] = []
        snapshot_dir: Path | None = None

        if run.worktree_path is not None and phase.commands:
            try:
                snapshot_dir = await _materialize_snapshot(run.worktree_path)
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                return PhaseResult(
                    success=False,
                    output=f"Error al materializar snapshot del worktree: {exc}",
                    termination_reason=TerminationReason.ERROR,
                )

        try:
            for i, cmd in enumerate(phase.commands):
                name = f"raise-runner-{run.run_id}-{i}-{uuid.uuid4().hex[:8]}"
                outcome = await self._run_one(cmd, run, name, snapshot_dir)
                all_output.extend(outcome.output_parts)
                if outcome.early_exit is not None:
                    return outcome.early_exit
                if not outcome.success:
                    return PhaseResult(
                        success=False,
                        output="".join(all_output),
                        termination_reason=TerminationReason.ERROR,
                    )
        finally:
            if snapshot_dir is not None:
                shutil.rmtree(snapshot_dir, ignore_errors=True)

        return PhaseResult(
            success=True,
            output="".join(all_output),
            termination_reason=TerminationReason.COMPLETED,
        )

    async def _run_one(
        self,
        cmd: str,
        run: PipelineRun,
        container_name: str,
        snapshot_dir: Path | None,
    ) -> _CmdOutcome:
        """Corre un solo comando en docker. Sin estado de instancia — thread-safe.

        Returns:
            _CmdOutcome con output_parts, success flag, y early_exit si hay error fatal
            que debe detenerse antes de agregar output (docker ausente, etc.).
        """
        args = _build_docker_args(cmd, run, self._image, snapshot_dir, container_name)
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            return _CmdOutcome(
                output_parts=[],
                success=False,
                early_exit=PhaseResult(
                    success=False,
                    output=f"docker no disponible: {exc}",
                    termination_reason=TerminationReason.ERROR,
                ),
            )
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return _CmdOutcome(
                output_parts=[],
                success=False,
                early_exit=PhaseResult(
                    success=False,
                    output=f"Error al iniciar docker: {exc}",
                    termination_reason=TerminationReason.ERROR,
                ),
            )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self._timeout
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            await self._kill_container(container_name)
            return _CmdOutcome(
                output_parts=[f"Timeout after {self._timeout}s: {cmd}"],
                success=False,
            )

        parts: list[str] = []
        if stdout:
            parts.append(stdout.decode())
        if stderr:
            parts.append(stderr.decode())
        return _CmdOutcome(output_parts=parts, success=proc.returncode == 0)

    async def _kill_container(self, container_name: str) -> None:
        """Mata un container por nombre vía ``docker kill`` (best-effort, AR-2).

        Si falla, el reaper de S2 (RAISE-10848) lo limpiará.
        """
        try:
            kill_proc = await asyncio.create_subprocess_exec(
                "docker",
                "kill",
                container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(kill_proc.communicate(), timeout=10.0)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning(
                "docker kill %s falló — el reaper de S2 lo limpiará",
                container_name,
            )
