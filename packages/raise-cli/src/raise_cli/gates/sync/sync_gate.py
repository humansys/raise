"""SyncGate — verifies local sync ledgers match remote state.

Discovers adapters implementing SyncVerifiable, verifies each ledger entry
via real GET requests against the remote. Keys must be provided explicitly
or --all used for full audit (decision HITL 2026-06-09).

Architecture: S-AQG.4 — Sync gate real verification
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import ClassVar

from raise_cli.adapters.models.sync import SyncReport
from raise_cli.adapters.protocols import SyncVerifiable
from raise_cli.exceptions import AdapterResolutionError
from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_SKIP_ENV = "RAISE_SYNC_SKIP_REASON"


def _discover_verifiable_adapters(
    working_dir: Path,
) -> tuple[list[SyncVerifiable], list[str]]:
    """Discover adapters implementing SyncVerifiable in connected mode.

    Returns (adapters, broken_descriptions).
    - Not configured (AdapterResolutionError) → skip silently (standalone).
    - Configured but broken (auth, network, corrupted config) → added to broken.
      Broken adapters cause the gate to FAIL — misconfiguration never masquerades
      as standalone (R3).
    - Only adapters with is_server_first=True are included (Q2) — standalone
      composites implement the protocol structurally but have no remote to verify.
    """
    from raise_cli.adapters.resolve import (
        build_docs_composite_for_gate,
        resolve_pm_adapter,
    )

    adapters: list[SyncVerifiable] = []
    broken: list[str] = []

    for domain, factory in (
        ("backlog", lambda: resolve_pm_adapter(None, working_dir)),
        ("docs", lambda: build_docs_composite_for_gate(working_dir)),
    ):
        try:
            adapter = factory()
        except AdapterResolutionError:
            continue  # not configured — legitimate standalone
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            broken.append(f"{domain}: {str(exc)[:120]}")
            continue

        if not isinstance(adapter, SyncVerifiable):
            continue
        if adapter.is_server_first:
            adapters.append(adapter)

    return adapters, broken


def _format_report(reports: list[SyncReport], unmatched: frozenset[str]) -> str:
    """Format verification results for human-readable gate output."""
    lines: list[str] = []
    total = sum(len(r.entries) for r in reports)
    exists_count = sum(1 for r in reports for e in r.entries if e.exists)

    if not unmatched and all(r.passed for r in reports):
        return f"gate-sync: all {total} entries verified"

    lines.append(f"gate-sync: {exists_count}/{total} entries verified")
    for r in reports:
        for e in r.entries:
            status = "✓" if e.exists else "✗"
            lines.append(f"  {r.domain}: {e.remote_key} {status} {e.detail}".rstrip())
        if r.pending_count > 0:
            lines.append(f"  {r.domain}: {r.pending_count} pending ops")
        if r.dead_letter_count > 0:
            lines.append(f"  {r.domain}: {r.dead_letter_count} dead-letter ops")
    for key in sorted(unmatched):
        lines.append(f"  {key}: not found in any sync ledger")

    return "\n".join(lines)


class SyncGate:
    """Gate that verifies local sync ledgers match remote state via real GETs.

    Keys must be passed explicitly or --all used for full ledger audit.
    Without keys, the gate fails loud (prevents silent pass on misconfiguration).

    Architecture: S-AQG.4, ADR-092
    """

    gate_id: ClassVar[str] = "gate-sync"
    description: ClassVar[str] = "Local sync ledgers match remote state"
    workflow_point: ClassVar[str] = "manual:sync"

    def evaluate(self, context: GateContext) -> GateResult:  # noqa: C901 — sequential early-return guards (workflow-point, skip-env, keys, broken/empty adapters, verification); splitting fragments the single evaluation contract
        """Evaluate sync parity for the given keys against the remote.

        Enforces only when invoked at this gate's own ``workflow_point`` (a direct
        ``rai gate check gate-sync`` or ``--point manual:sync``). Under a blanket
        ``rai gate check --all`` sweep (``workflow_point=None``) the gate skips
        with a clear reason instead of failing-loud on missing keys (RAISE-10723).
        """
        if context.workflow_point != self.workflow_point:
            return GateResult(
                gate_id=self.gate_id,
                passed=True,
                message=(
                    f"skipped: sync verification runs at {self.workflow_point}, "
                    "not in this context"
                ),
            )

        skip = os.environ.get(_SKIP_ENV)
        if skip:
            return GateResult(
                gate_id=self.gate_id, passed=True, message=f"Skipped: {skip}"
            )

        # Keys explicit or --all — never implicit (decision HITL 2026-06-09)
        args = list(context.extra_args)
        verify_all = "--all" in args
        keys = frozenset(a for a in args if a != "--all")
        if not keys and not verify_all:
            return GateResult(
                gate_id=self.gate_id,
                passed=False,
                message="no keys provided — pass keys or use --all",
            )
        scope_keys: frozenset[str] | None = None if verify_all else keys

        adapters, broken = _discover_verifiable_adapters(context.working_dir)
        if broken:
            return GateResult(
                gate_id=self.gate_id,
                passed=False,
                message="adapter construction failed: " + "; ".join(broken),
            )
        if not adapters:
            return GateResult(
                gate_id=self.gate_id,
                passed=True,
                message="No verifiable adapters found (standalone mode)",
            )

        reports = [a.verify_sync(scope_keys) for a in adapters]

        # C1: keys requested but not found in any entry → FAIL
        unmatched: frozenset[str] = frozenset()
        if scope_keys is not None:
            matched = {
                k
                for r in reports
                for e in r.entries
                for k in (e.local_key, e.remote_key)
            }
            unmatched = scope_keys - matched

        all_passed = all(r.passed for r in reports) and not unmatched
        message = _format_report(reports, unmatched)

        detail_lines: list[str] = []
        for r in reports:
            for e in r.entries:
                if not e.exists:
                    detail_lines.append(
                        f"{r.domain}: {e.remote_key} missing — {e.detail}"
                    )
        for key in sorted(unmatched):
            detail_lines.append(f"unmatched: {key} not found in any sync ledger")

        return GateResult(
            gate_id=self.gate_id,
            passed=all_passed,
            message=message,
            details=tuple(detail_lines),
        )
