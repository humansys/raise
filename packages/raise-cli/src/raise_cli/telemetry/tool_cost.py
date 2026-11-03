"""Multi-tool cost adapter — S16430.2 (RAISE-16690).

Builds `tool_cost` events for AI tools other than raise-cli (Copilot, Cursor,
IBM Bob, ...) and resolves USD normalization at emission time (SD2, never at
query time): ``--usd-rate`` flag > ``.raise/cost-rates.yaml`` > no rate.

The event_id is deterministic per (tool_name, unit, date, note) — re-ingesting
the same (tool, unit, day) is a safe idempotent no-op (409 on the server).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

_DEFAULT_CONFIG_PATH = Path(".raise/cost-rates.yaml")


def _resolve_usd_rate(
    tool_name: str,
    unit: str,
    *,
    usd_rate: float | None = None,
    config_path: Path | None = None,
) -> float | None:
    """Resolve a native-unit -> USD rate.

    Resolution order (SD2): ``unit == "USD"`` always resolves to 1.0 (the
    amount already IS the USD cost), then the explicit ``usd_rate`` argument,
    then ``.raise/cost-rates.yaml`` (``rates: {tool: {unit: usd_per_unit}}``),
    then ``None`` (no normalization possible — cost_usd is omitted).
    """
    if unit == "USD":
        return 1.0
    if usd_rate is not None:
        return usd_rate

    path = config_path if config_path is not None else _DEFAULT_CONFIG_PATH
    if not path.exists():
        return None
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    rates: Any = data.get("rates")
    if not isinstance(rates, dict):
        return None
    tool_rates: Any = rates.get(tool_name)
    if not isinstance(tool_rates, dict):
        return None
    rate: Any = tool_rates.get(unit)
    if isinstance(rate, bool) or not isinstance(rate, (int, float)):
        return None
    return float(rate)


def build_tool_cost_event(
    tool_name: str,
    amount: float,
    *,
    unit: str = "USD",
    date: str | None = None,
    usd_rate: float | None = None,
    note: str | None = None,
    repo_slug: str | None = None,
    work_item_ref: str | None = None,
    config_path: Path | None = None,
) -> AgentEventCreate:
    """Build a `tool_cost` AgentEventCreate from a manual cost ingestion (SD1).

    Args:
        tool_name: Slug lowercase (e.g. "copilot", "cursor", "ibm-bob").
        amount: Cost amount in native unit (> 0).
        unit: Native unit ("USD" | "tokens" | "credits" | other — open set).
        date: ISO date string (YYYY-MM-DD). Defaults to today UTC.
        usd_rate: Explicit USD-per-unit rate (overrides config file).
        note: Optional discriminator for a second event on the same
            (tool, unit, day) — feeds event_id idempotency.
        repo_slug: Optional project identifier.
        work_item_ref: Optional Jira key for work attribution.
        config_path: Override for the rate config file (testing hook).
    """
    if amount <= 0:
        msg = f"amount must be > 0, got {amount}"
        raise ValueError(msg)
    tool_name = tool_name.lower()
    if date is None:
        date = datetime.now(UTC).strftime("%Y-%m-%d")

    rate = _resolve_usd_rate(
        tool_name, unit, usd_rate=usd_rate, config_path=config_path
    )
    cost_usd = amount * rate if rate is not None else None

    event_id = make_event_id(
        event_type="tool_cost",
        work_item_ref=work_item_ref,
        iso_timestamp=date,
        source_id=f"{tool_name}:{unit}:{note or ''}",
    )

    payload: dict[str, object] = {
        "tool_name": tool_name,
        "amount": amount,
        "unit": unit,
        "date": date,
    }
    if cost_usd is not None:
        payload["cost_usd"] = cost_usd
    if repo_slug is not None:
        payload["repo_slug"] = repo_slug
    if note is not None:
        payload["note"] = note

    return AgentEventCreate(
        event_type="tool_cost",
        payload=payload,
        work_item_ref=work_item_ref,
        event_id=event_id,
    )
