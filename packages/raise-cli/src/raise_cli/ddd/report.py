"""DDD classification HTML report generator."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from raise_cli.ddd.classifier import ClassificationResult

if TYPE_CHECKING:
    from raise_cli.ddd.pipeline import ClassifyReport, ModuleDensity

BULK_CONFIRM_MIN_ROWS = 3
BULK_CONFIRM_MAJORITY_RATIO = 0.8


def _confidence_color(confidence: float) -> str:
    if confidence >= 0.8:
        return "#4caf50"
    if confidence >= 0.7:
        return "#ff9800"
    return "#f44336"


def _module_context_str(module_id: str, densities: dict[str, ModuleDensity]) -> str:
    """Build the `mod-x (D: 92%, I: 6%, ?: 2%)` string, with a graceful fallback."""
    density = densities.get(module_id)
    if density is None or density.total_accepted == 0:
        return f"{module_id} (no density data)"
    total = density.total_accepted
    pct_d = density.count_d / total
    pct_i = density.count_i / total
    pct_unknown = max(0.0, (total - density.count_d - density.count_i) / total)
    return f"{module_id} (D: {pct_d:.0%}, I: {pct_i:.0%}, ?: {pct_unknown:.0%})"


def _group_uncertain_by_module(
    uncertain_results: list[ClassificationResult],
    module_by_symbol: dict[str, str],
) -> list[tuple[str, list[ClassificationResult]]]:
    """Group uncertain results by module, sorted per DD3.

    Groups are ordered by ascending minimum confidence within the group;
    rows are ordered ascending by confidence within each group. Symbols
    with no module mapping fall into a trailing "(unknown module)" group.
    """
    groups: dict[str, list[ClassificationResult]] = {}
    for r in uncertain_results:
        mod = module_by_symbol.get(r.id) or "(unknown module)"
        groups.setdefault(mod, []).append(r)

    ordered: list[tuple[str, list[ClassificationResult]]] = [
        (mod, sorted(rows, key=lambda r: r.confidence)) for mod, rows in groups.items()
    ]
    ordered.sort(key=lambda item: min(r.confidence for r in item[1]))
    return ordered


def _bulk_confirm_layer(rows: list[ClassificationResult]) -> str | None:
    """Return the majority layer if the group qualifies for bulk-confirm (DD4).

    Only D and I layers count — ambiguous (?) rows are excluded from the
    majority calculation to prevent false ratifications (F1 review fix).
    """
    if len(rows) < BULK_CONFIRM_MIN_ROWS:
        return None
    counts: dict[str, int] = {}
    for r in rows:
        if r.ddd_layer in ("D", "I"):
            counts[r.ddd_layer] = counts.get(r.ddd_layer, 0) + 1
    if not counts:
        return None
    layer, count = max(counts.items(), key=lambda kv: kv[1])
    if count / len(rows) >= BULK_CONFIRM_MAJORITY_RATIO:
        return layer
    return None


def _render_hitl_row(r: ClassificationResult, module_id: str, context_str: str) -> str:
    color = _confidence_color(r.confidence)
    return (
        f'<tr data-symbol-id="{html.escape(r.id)}" data-module="{html.escape(module_id)}" '
        f'data-layer="{html.escape(r.ddd_layer)}" data-confidence="{r.confidence:.2f}">'
        f'<td><input type="checkbox" class="sym-confirm"></td>'
        f"<td>{html.escape(r.id)}</td>"
        f"<td>{html.escape(r.ddd_layer)}</td>"
        f'<td style="color:{color};font-weight:bold">{r.confidence:.2f}</td>'
        f"<td>{html.escape(context_str)}</td>"
        f"<td>{html.escape(r.reasoning)}</td>"
        f"</tr>"
    )


def _render_hitl_header(
    module_id: str, rows: list[ClassificationResult], context_str: str
) -> str:
    confirm_layer = _bulk_confirm_layer(rows)
    confirm_attr = ""
    button = ""
    if confirm_layer:
        confirm_attr = f' data-confirm-layer="{html.escape(confirm_layer)}"'
        button = (
            f'<button class="bulk-confirm" type="button">'
            f"Confirm all as {html.escape(confirm_layer)}</button>"
        )
    return (
        f'<tr class="module-header" data-module="{html.escape(module_id)}"{confirm_attr}>'
        f'<td colspan="6">{html.escape(context_str)} — {len(rows)} symbols '
        f"{button}</td>"
        f"</tr>"
    )


def _render_hitl_section(report: ClassifyReport) -> str:
    """Render the HITL review section (above the classified table, DD6).

    Returns "" when there are no uncertain results (backward compat, AC9).
    """
    if not report.uncertain_results:
        return ""

    ordered_groups = _group_uncertain_by_module(
        report.uncertain_results, report.module_by_symbol
    )

    blocks: list[str] = []
    for module_id, rows in ordered_groups:
        context_str = _module_context_str(module_id, report.module_densities)
        blocks.append(_render_hitl_header(module_id, rows, context_str))
        blocks.extend(_render_hitl_row(r, module_id, context_str) for r in rows)

    rows_html = "\n".join(blocks)

    # NOTE (DR2): the export button below builds a JSON array shaped
    # {module, classification, reasoning, symbols, source} from checked
    # rows. This shape is pinned by the contract test
    # test_export_shape_parses_via_parse_domain_context in
    # tests/ddd/test_report_enhanced_hitl.py — keep the two in lockstep.
    return f"""
<h2>HITL Review — Uncertain Symbols</h2>
<div id="hitl-summary" class="summary-bar">0 confirmed, {len(report.uncertain_results)} flagged</div>
<table id="hitl-table">
<thead>
<tr><th></th><th>Symbol ID</th><th>Layer</th><th>Confidence</th><th>Module Context</th><th>Reasoning</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
<button id="export-btn" type="button">Export Decisions</button>
<script>
(function () {{
  var table = document.getElementById('hitl-table');
  if (!table) return;
  var summary = document.getElementById('hitl-summary');
  var exportBtn = document.getElementById('export-btn');

  function updateSummary() {{
    var checked = table.querySelectorAll('input.sym-confirm:checked').length;
    var total = table.querySelectorAll('input.sym-confirm').length;
    summary.textContent = checked + ' confirmed, ' + (total - checked) + ' flagged';
  }}

  function setRowRatified(checkbox, ratified) {{
    var row = checkbox.closest('tr');
    if (!row) return;
    checkbox.checked = ratified;
    row.classList.toggle('ratified', ratified);
  }}

  table.addEventListener('change', function (evt) {{
    var target = evt.target;
    if (target.classList && target.classList.contains('sym-confirm')) {{
      setRowRatified(target, target.checked);
      updateSummary();
    }}
  }});

  table.addEventListener('click', function (evt) {{
    var target = evt.target;
    if (target.classList && target.classList.contains('bulk-confirm')) {{
      var headerRow = target.closest('tr');
      var moduleId = headerRow.getAttribute('data-module');
      var rows = table.querySelectorAll(
        'tr[data-module="' + moduleId + '"]:not(.module-header)'
      );
      rows.forEach(function (row) {{
        var cb = row.querySelector('input.sym-confirm');
        if (cb) setRowRatified(cb, true);
      }});
      updateSummary();
    }}
  }});

  exportBtn.addEventListener('click', function () {{
    var byModule = {{}};
    table.querySelectorAll('tr[data-symbol-id]').forEach(function (row) {{
      var cb = row.querySelector('input.sym-confirm');
      if (!cb || !cb.checked) return;
      var moduleId = row.getAttribute('data-module');
      var layer = row.getAttribute('data-layer');
      var symbolId = row.getAttribute('data-symbol-id');
      if (!byModule[moduleId]) byModule[moduleId] = {{ D: 0, I: 0, symbols: [] }};
      byModule[moduleId][layer] = (byModule[moduleId][layer] || 0) + 1;
      byModule[moduleId].symbols.push(symbolId);
    }});
    var decisions = [];
    var totalInModule = {{}};
    table.querySelectorAll('tr[data-symbol-id]').forEach(function (row) {{
      var mid = row.getAttribute('data-module');
      totalInModule[mid] = (totalInModule[mid] || 0) + 1;
    }});
    Object.keys(byModule).forEach(function (moduleId) {{
      var entry = byModule[moduleId];
      var confirmed = entry.symbols.length;
      var confirmedD = entry.D || 0;
      var confirmedI = entry.I || 0;
      if (confirmedD === 0 && confirmedI === 0) return;
      var groupTotal = totalInModule[moduleId] || confirmed;
      var classification = confirmedD >= confirmedI ? 'domain' : 'infra';
      var majorityLayer = classification === 'domain' ? 'D' : 'I';
      decisions.push({{
        module: moduleId,
        classification: classification,
        reasoning: 'HITL: ' + confirmed + '/' + groupTotal +
          ' uncertain symbols confirmed as ' + majorityLayer + '; ' +
          confirmedD + ' D, ' + confirmedI + ' I',
        symbols: entry.symbols,
        source: 'hitl-confirm'
      }});
    }});
    var blob = new Blob([JSON.stringify(decisions, null, 2)], {{ type: 'application/json' }});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'ddd-decisions.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }});
}})();
</script>
"""


def _render_domain_context_section(domain_context: str | None) -> str:
    """Render a collapsible <details> section for Pass 1 BC→module hints.

    RAISE-16788: only rendered when ClassifyReport.domain_context is not None.
    """
    if not domain_context:
        return ""
    escaped_lines = html.escape(domain_context)
    return (
        "\n<details>\n"
        "<summary><strong>Domain Context Hints</strong> (injected into Pass 1 prompt)</summary>\n"
        f"<pre style='background:#f5f5f5;padding:1rem;border-radius:4px;margin-top:0.5rem'>"
        f"{escaped_lines}</pre>\n"
        "</details>\n"
    )


def render_html_report(report: ClassifyReport) -> str:
    """Render a ClassifyReport as a standalone HTML page."""
    rows: list[str] = []
    for r in report.results:
        color = _confidence_color(r.confidence)
        rows.append(
            f"<tr>"
            f"<td>{html.escape(r.id)}</td>"
            f"<td>{html.escape(r.ddd_layer)}</td>"
            f'<td style="color:{color};font-weight:bold">{r.confidence:.2f}</td>'
            f"<td>{html.escape(r.reasoning)}</td>"
            f"</tr>"
        )

    table_body = "\n".join(rows) if rows else "<tr><td colspan='4'>No results</td></tr>"
    hitl_section = _render_hitl_section(report)
    domain_context_section = _render_domain_context_section(report.domain_context)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DDD Classification Report</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #fafafa; }}
h1 {{ color: #333; }}
h2 {{ color: #333; margin-top: 2rem; }}
.summary {{ display: flex; gap: 1.5rem; margin: 1rem 0; flex-wrap: wrap; }}
.card {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.5rem; min-width: 120px; }}
.card .label {{ font-size: 0.85rem; color: #666; }}
.card .value {{ font-size: 1.5rem; font-weight: bold; color: #333; }}
table {{ border-collapse: collapse; width: 100%; background: #fff; margin-top: 1rem; }}
th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }}
th {{ background: #f5f5f5; font-weight: 600; }}
tr:hover {{ background: #f9f9f9; }}
.module-header td {{ background: #e3f2fd; font-weight: 600; }}
.ratified {{ background: #c8e6c9; }}
.summary-bar {{ font-weight: 600; margin: 0.5rem 0; }}
.bulk-confirm {{ margin-left: 1rem; }}
#export-btn {{ margin-top: 1rem; }}
</style>
</head>
<body>
<h1>DDD Classification Report</h1>
<div class="summary">
  <div class="card"><div class="label">Total</div><div class="value">{report.total}</div></div>
  <div class="card"><div class="label">Classified</div><div class="value">{report.classified}</div></div>
  <div class="card"><div class="label">Skipped</div><div class="value">{report.skipped}</div></div>
  <div class="card"><div class="label">Escalated</div><div class="value">{report.escalated}</div></div>
  <div class="card"><div class="label">Domain (D)</div><div class="value" style="color:#4caf50">{report.count_d}</div></div>
  <div class="card"><div class="label">Infra (I)</div><div class="value" style="color:#2196f3">{report.count_i}</div></div>
  <div class="card"><div class="label">Ambiguous (?)</div><div class="value" style="color:#ff9800">{report.count_ambiguous}</div></div>
</div>
{domain_context_section}{hitl_section}
<table>
<thead>
<tr><th>Symbol ID</th><th>Layer</th><th>Confidence</th><th>Reasoning</th></tr>
</thead>
<tbody>
{table_body}
</tbody>
</table>
</body>
</html>"""
