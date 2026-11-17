"""LaTeX table reporter for evaluation results."""

from __future__ import annotations

from raise_cli.eval._models import EvalResult


class LaTeXReporter:
    """Render EvalResult as a LaTeX tabular environment."""

    def render(self, result: EvalResult) -> str:
        """Produce LaTeX table with per-query metrics and mean row."""
        if not result.per_query:
            return "% No evaluation results.\n"

        metrics = sorted(next(iter(result.per_query.values())).keys())
        col_spec = "l" + "r" * len(metrics)

        lines: list[str] = []
        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        lines.append("\\toprule")
        lines.append("Query & " + " & ".join(metrics) + " \\\\")
        lines.append("\\midrule")

        for qid in sorted(result.per_query):
            vals = result.per_query[qid]
            row = (
                f"{qid} & "
                + " & ".join(f"{vals.get(m, 0.0):.4f}" for m in metrics)
                + " \\\\"
            )
            lines.append(row)

        lines.append("\\midrule")
        mean_row = (
            "\\textbf{Mean} & "
            + " & ".join(f"{result.metrics.get(m, 0.0):.4f}" for m in metrics)
            + " \\\\"
        )
        lines.append(mean_row)
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")

        return "\n".join(lines) + "\n"
