"""Markdown table reporter for evaluation results."""

from __future__ import annotations

from raise_cli.eval._models import EvalResult


class MarkdownReporter:
    """Render EvalResult as a markdown table."""

    def render(self, result: EvalResult) -> str:
        """Produce markdown table with per-query metrics and mean row."""
        if not result.per_query:
            return "No evaluation results.\n"

        metrics = sorted(next(iter(result.per_query.values())).keys())
        header = "| Query | " + " | ".join(metrics) + " |"
        separator = "|" + "|".join("------" for _ in range(len(metrics) + 1)) + "|"

        rows: list[str] = [header, separator]
        for qid in sorted(result.per_query):
            vals = result.per_query[qid]
            row = (
                f"| {qid} | "
                + " | ".join(f"{vals.get(m, 0.0):.4f}" for m in metrics)
                + " |"
            )
            rows.append(row)

        mean_row = (
            "| **Mean** | "
            + " | ".join(f"{result.metrics.get(m, 0.0):.4f}" for m in metrics)
            + " |"
        )
        rows.append(mean_row)

        return "\n".join(rows) + "\n"
