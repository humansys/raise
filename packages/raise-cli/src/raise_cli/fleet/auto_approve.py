"""Fleet auto-approve evaluator.

Pure function with no I/O — all config loading happens in config.load().
"""

from __future__ import annotations

from raise_cli.fleet.config import FleetConfig


def evaluate_auto_approve(config: FleetConfig, size: str, gate_passed: bool) -> bool:
    """Evaluate whether a story qualifies for automatic approval.

    Returns True ONLY when:
    - gate_passed is True, AND
    - at least one rule in config matches the story size (or has size=None wildcard).

    Returns False when config has no rules, no rule matches, or gate_passed is False.

    Args:
        config: Fleet configuration with auto-approve rules.
        size: Story size string (e.g., "xs", "XS"). Comparison is case-insensitive.
        gate_passed: True when all pipeline gates have passed.

    Returns:
        True if auto-approve should proceed; False otherwise.
    """
    if not gate_passed:
        return False
    size_lower = size.lower()
    for rule in config.auto_approve.rules:
        rule_size = rule.size  # already lowercased by validator (or None)
        if rule_size is None or rule_size == size_lower:
            return True
    return False
