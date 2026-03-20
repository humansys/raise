"""Doctor check runner — executes checks in pipeline order.

Pipeline order ensures dependencies: environment must pass before
project checks, project before adapters, etc.
"""

from __future__ import annotations

import logging

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.registry import CheckRegistry

logger = logging.getLogger(__name__)

PIPELINE_ORDER: list[str] = [
    "environment",
    "developer",
    "project",
    "acli",
    "adapters",
    "skills",
    "mcp",
]


def run_checks(
    registry: CheckRegistry,
    context: DoctorContext,
    categories: list[str] | None = None,
) -> list[CheckResult]:
    """Execute checks in pipeline order.

    Args:
        registry: Check registry with discovered checks.
        context: Execution context (working_dir, online, verbose).
        categories: If provided, only run checks in these categories.

    Returns:
        All check results in execution order.
    """
    results: list[CheckResult] = []
    critical_failure = False

    ordered = categories or PIPELINE_ORDER

    for category in ordered:
        if critical_failure:
            results.append(
                CheckResult(
                    check_id=f"{category}-skipped",
                    category=category,
                    status=CheckStatus.WARN,
                    message="Skipped — previous category had critical errors",
                )
            )
            continue

        checks = registry.get_checks_for_category(category)
        if not checks:
            continue

        for check in checks:
            if check.requires_online and not context.online:
                logger.debug("Skipping online check '%s'", check.check_id)
                continue

            try:
                check_results = check.evaluate(context)
                results.extend(check_results)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Check '%s' raised: %s", check.check_id, exc)
                results.append(
                    CheckResult(
                        check_id=check.check_id,
                        category=check.category,
                        status=CheckStatus.ERROR,
                        message=f"Check crashed: {exc}",
                    )
                )

        # If any ERROR in this category, flag for downstream skip
        category_errors = [
            r
            for r in results
            if r.category == category and r.status == CheckStatus.ERROR
        ]
        if category_errors and category == "environment":
            critical_failure = True

    return results


def summarize(results: list[CheckResult]) -> tuple[int, int, int]:
    """Count pass/warn/error results. Returns (pass_count, warn_count, error_count)."""
    passes = sum(1 for r in results if r.status == CheckStatus.PASS)
    warns = sum(1 for r in results if r.status == CheckStatus.WARN)
    errors = sum(1 for r in results if r.status == CheckStatus.ERROR)
    return passes, warns, errors
