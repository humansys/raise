"""Shared manifest-driven gate runner.

Reads a command from ``.raise/manifest.yaml`` and executes it via subprocess.
All built-in gates delegate to this helper for DRY command execution.

Architecture: S474.2 — Configurable Gates + FormatGate
"""

from __future__ import annotations

import subprocess

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.onboarding.manifest import load_manifest


def run_manifest_command(
    gate_id: str,
    manifest_key: str,
    description: str,
    context: GateContext,
) -> GateResult:
    """Read a command from manifest and execute it.

    Args:
        gate_id: Unique gate identifier (e.g. ``"gate-tests"``).
        manifest_key: Attribute name on ``ProjectInfo`` (e.g. ``"test_command"``).
        description: Human-readable description for pass messages.
        context: Gate evaluation context with working directory.

    Returns:
        GateResult with pass/fail/skip outcome.
    """
    manifest = load_manifest(context.working_dir)
    if manifest is None:
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message="No .raise/manifest.yaml found",
        )

    command: str | None = getattr(manifest.project, manifest_key, None)
    if command is None:
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"Skipped — {manifest_key} not configured",
        )

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=str(context.working_dir),
        )
    except Exception as exc:  # noqa: BLE001
        return GateResult(
            passed=False,
            gate_id=gate_id,
            message=f"{type(exc).__name__}: {exc}",
        )

    passed = result.returncode == 0
    return GateResult(
        passed=passed,
        gate_id=gate_id,
        message=description if passed else f"{description} failed",
        details=tuple(s for s in (result.stdout, result.stderr) if s)
        if not passed
        else (),
    )
