"""CLI for evaluation harness — rai eval run, rai eval tune."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console

from raise_cli.eval._paths import FIXTURES_DIR

if TYPE_CHECKING:
    from raise_cli.eval._models import TuningResult

eval_app = typer.Typer(
    name="eval",
    help="Evaluation harness for retrieval quality.",
    no_args_is_help=True,
)

console = Console()


class OutputFormat(str, Enum):
    """Evaluation report output format."""

    markdown = "markdown"
    latex = "latex"
    json = "json"


def _load_suite_corpus(
    fixtures: Path, suite: str
) -> tuple[list[dict[str, object]], str]:
    """Resolve the corpus and thresholds file for a suite.

    The ``union`` suite (S-KC7.10) adds the frozen cross-cartridge
    distractors to the annotated corpus and uses its own thresholds —
    a regression guard for cross-cartridge interference.
    """
    from raise_cli.eval.datasets import load_corpus

    corpus = load_corpus(fixtures / "corpus.json")
    if suite == "union":
        corpus = corpus + load_corpus(fixtures / "corpus-distractors.json.gz")
        return corpus, "thresholds-union.json"
    if suite == "federated":
        return load_corpus(
            fixtures / "corpus-federated.json.gz"
        ), "thresholds-federated.json"
    return corpus, "thresholds.json"


@eval_app.command()
def run(
    suite: Annotated[str, typer.Option(help="Evaluation suite name")] = "cartridge",
    fmt: Annotated[
        OutputFormat, typer.Option("--format", help="Output format")
    ] = OutputFormat.markdown,
    baseline: Annotated[
        Path | None, typer.Option(help="Baseline JSON for comparison")
    ] = None,
    output: Annotated[Path | None, typer.Option(help="Write output to file")] = None,
) -> None:
    """Run evaluation suite against corpus fixtures."""
    from raise_cli.eval import run_eval
    from raise_cli.eval.datasets import load_qrels, load_queries
    from raise_cli.eval.reporters.json_report import JsonReporter
    from raise_cli.eval.reporters.latex import LaTeXReporter
    from raise_cli.eval.reporters.markdown import MarkdownReporter

    fixtures = Path.cwd() / FIXTURES_DIR
    if not fixtures.exists():
        console.print("[red]No eval fixtures found at[/red]", str(fixtures))
        raise typer.Exit(code=1)

    if suite == "federated":
        qrels = load_qrels(fixtures / "qrels-federated.tsv")
        queries = load_queries(fixtures / "queries-federated.json")
    else:
        qrels = load_qrels(fixtures / "qrels.tsv")
        queries = load_queries(fixtures / "queries.json")
    corpus, thresholds_file = _load_suite_corpus(fixtures, suite)

    thresholds: dict[str, float] | None = None
    if baseline is not None:
        import json

        thresholds = json.loads(baseline.read_text(encoding="utf-8"))
    elif (fixtures / thresholds_file).exists():
        import json

        thresholds = json.loads(
            (fixtures / thresholds_file).read_text(encoding="utf-8")
        )

    if suite == "federated":
        from raise_cli.eval.harness import run_federated_eval_impl

        result = run_federated_eval_impl(
            qrels=qrels,
            corpus=corpus,
            queries=queries,
            suite=suite,
            thresholds=thresholds,
        )
    else:
        result = run_eval(
            qrels=qrels,
            corpus=corpus,
            queries=queries,
            suite=suite,
            thresholds=thresholds,
            # Mirror EvalGate + production: the real cartridge adapter
            # (seeds/SA/domain) is part of the retrieval being measured.
            # Neutral adapter under-represents prod (RAISE-11208).
            use_cartridge_adapter=True,
        )

    reporters = {
        OutputFormat.markdown: MarkdownReporter,
        OutputFormat.latex: LaTeXReporter,
        OutputFormat.json: JsonReporter,
    }
    reporter = reporters[fmt]()
    rendered = reporter.render(result)

    if output is not None:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {output}")
    else:
        console.print(rendered)


def _render_tuning_markdown(
    results: list[TuningResult],
    baseline_weights: tuple[float, ...],
) -> str:
    """Render tuning results as a markdown table."""
    ndim = len(results[0].weights) if results else 3
    if ndim >= 4:
        header = "| W_SA | W_ATTR | W_DOMAIN | W_SEM | NDCG@10 | MRR | MAP | P@5 |"
        sep = "|------|--------|----------|-------|---------|-----|-----|-----|"
    else:
        header = "| W_SA | W_ATTR | W_DOMAIN | NDCG@10 | MRR | MAP | P@5 |"
        sep = "|------|--------|----------|---------|-----|-----|-----|"
    lines: list[str] = ["## Weight Tuning Results\n", header, sep]
    for r in results:
        w = r.weights
        m = r.metrics
        marker = " ← baseline" if w == baseline_weights else ""
        w_cols = f"| {w[0]:.1f} | {w[1]:.1f} | {w[2]:.1f} "
        if ndim >= 4:
            w_cols += f"| {w[3]:.1f} "
        lines.append(
            f"{w_cols}"
            f"| {m.get('ndcg@10', 0):.4f} "
            f"| {m.get('mrr', 0):.4f} "
            f"| {m.get('map', 0):.4f} "
            f"| {m.get('precision@5', 0):.4f} |{marker}"
        )
    return "\n".join(lines) + "\n"


@eval_app.command()
def recalibrate(
    cartridge_dir: Annotated[
        Path, typer.Option(help="Cartridge root directory (default: CWD)")
    ] = Path("."),
    margin: Annotated[
        float, typer.Option(help="Safety margin fraction (default 5%)")
    ] = 0.05,
) -> None:
    """Recalibrate thresholds.json from current hybrid scorer metrics.

    Runs the eval harness against the cartridge's eval/ fixtures using the
    same hybrid scorer EvalGate would use, then derives thresholds as
    ``metric * (1 - margin)`` and writes them to eval/thresholds.json.
    """
    from raise_cli.eval.recalibrate import recalibrate_cartridge

    cartridge_path = cartridge_dir.resolve()
    try:
        thresholds = recalibrate_cartridge(cartridge_path, margin=margin)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Thresholds written to {cartridge_path / 'eval' / 'thresholds.json'}[/green]"
    )
    for metric, value in thresholds.items():
        console.print(f"  {metric}: {value:.3f}")


@eval_app.command()
def tune(
    step: Annotated[float, typer.Option(help="Grid step size (e.g. 0.1)")] = 0.1,
    ndim: Annotated[int, typer.Option(help="Number of weight dimensions (3 or 4)")] = 3,
    fmt: Annotated[
        OutputFormat, typer.Option("--format", help="Output format")
    ] = OutputFormat.markdown,
    output: Annotated[Path | None, typer.Option(help="Write output to file")] = None,
) -> None:
    """Run weight tuning grid search over scoring weights."""
    from raise_cli.eval.datasets import load_corpus, load_qrels, load_queries
    from raise_cli.eval.tuning import grid_search
    from raise_core.graph.scorers import InMemorySemanticScorer

    fixtures = Path.cwd() / FIXTURES_DIR
    if not fixtures.exists():
        console.print("[red]No eval fixtures found at[/red]", str(fixtures))
        raise typer.Exit(code=1)

    qrels = load_qrels(fixtures / "qrels.tsv")
    corpus = load_corpus(fixtures / "corpus.json")
    queries = load_queries(fixtures / "queries.json")

    scorer = InMemorySemanticScorer(corpus) if ndim >= 4 else None

    console.print(f"[bold]Running {ndim}D grid search with step={step}...[/bold]")
    results = grid_search(
        qrels=qrels,
        corpus=corpus,
        queries=queries,
        step=step,
        ndim=ndim,
        semantic_scorer=scorer,
    )
    console.print(f"[green]Evaluated {len(results)} weight combinations.[/green]")

    from raise_core.graph.retrieval.engine import W_ATTR, W_DOMAIN, W_SA, W_SEM

    baseline_weights: tuple[float, ...] = (
        (W_SA, W_ATTR, W_DOMAIN, W_SEM) if ndim >= 4 else (W_SA, W_ATTR, W_DOMAIN)
    )

    if fmt == OutputFormat.markdown:
        rendered = _render_tuning_markdown(results, baseline_weights)
    else:
        import json

        rendered = json.dumps(
            [{"weights": list(r.weights), "metrics": r.metrics} for r in results],
            indent=2,
        )

    if output is not None:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {output}")
    else:
        console.print(rendered)
