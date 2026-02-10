"""Generate self-contained interactive HTML visualization of the memory graph.

Reads the NetworkX-compatible index.json and produces a single HTML file
with an embedded D3.js force-directed graph. No external dependencies at runtime.
"""

from __future__ import annotations

import json
from pathlib import Path

# D3 v7 minified is ~270KB — we load from CDN for now to keep the file small.
# The HTML is still self-contained in that it has no server dependency.

_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>RaiSE Memory Graph</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; overflow: hidden; }
  #controls { position: fixed; top: 12px; left: 12px; z-index: 10; display: flex; flex-wrap: wrap; gap: 6px; max-width: 80vw; }
  .chip { padding: 4px 10px; border-radius: 12px; font-size: 12px; cursor: pointer; border: 1px solid #30363d; background: #161b22; transition: all 0.15s; user-select: none; }
  .chip:hover { border-color: #58a6ff; }
  .chip.active { border-color: #58a6ff; background: #1f2937; color: #58a6ff; }
  .chip .count { opacity: 0.5; margin-left: 4px; }
  #info { position: fixed; bottom: 12px; left: 12px; z-index: 10; font-size: 11px; color: #484f58; }
  #tooltip { position: fixed; pointer-events: none; z-index: 20; background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 10px 14px; font-size: 12px; max-width: 400px; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
  #tooltip .tt-id { font-weight: 600; color: #58a6ff; margin-bottom: 4px; }
  #tooltip .tt-type { font-size: 11px; color: #8b949e; margin-bottom: 6px; }
  #tooltip .tt-content { color: #c9d1d9; line-height: 1.4; max-height: 120px; overflow: hidden; }
  #search { position: fixed; top: 12px; right: 12px; z-index: 10; padding: 6px 12px; border-radius: 8px; border: 1px solid #30363d; background: #161b22; color: #c9d1d9; font-size: 13px; width: 220px; outline: none; }
  #search:focus { border-color: #58a6ff; }
  #search::placeholder { color: #484f58; }
  svg { width: 100vw; height: 100vh; }
</style>
</head>
<body>
<div id="controls"></div>
<input id="search" type="text" placeholder="Search nodes..." />
<div id="tooltip"><div class="tt-id"></div><div class="tt-type"></div><div class="tt-content"></div></div>
<div id="info"></div>
<svg></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
// --- DATA (injected by generator) ---
const graphData = %%GRAPH_DATA%%;

// --- COLOR PALETTE by node type ---
const typeColors = {
  component: '#3fb950', pattern: '#a371f7', session: '#d29922', calibration: '#f0883e',
  story: '#58a6ff', epic: '#1f6feb', term: '#8b949e', principle: '#f778ba',
  decision: '#db6d28', guardrail: '#f85149', skill: '#79c0ff', module: '#56d364',
  bounded_context: '#7ee787', requirement: '#d2a8ff', layer: '#388bfd', architecture: '#3fb950',
  outcome: '#a5d6ff', project: '#ffd33d'
};
const defaultColor = '#484f58';
function color(type) { return typeColors[type] || defaultColor; }

// --- PREP DATA ---
const nodeMap = new Map(graphData.nodes.map(n => [n.id, n]));
const typeCounts = {};
graphData.nodes.forEach(n => { typeCounts[n.type] = (typeCounts[n.type] || 0) + 1; });

// For large graphs, sample edges to keep it interactive
let links = graphData.links || graphData.edges || [];
const MAX_EDGES = 3000;
if (links.length > MAX_EDGES) {
  // Prioritize non-related_to edges, then sample related_to
  const important = links.filter(l => l.type !== 'related_to');
  const relatedTo = links.filter(l => l.type === 'related_to');
  const remaining = MAX_EDGES - important.length;
  const sampled = relatedTo.sort(() => Math.random() - 0.5).slice(0, Math.max(0, remaining));
  links = [...important, ...sampled];
}

// Resolve links to node references
const nodes = graphData.nodes.map(n => ({...n}));
const nodeIdx = new Map(nodes.map((n, i) => [n.id, i]));
const resolvedLinks = [];
links.forEach(l => {
  const s = l.source.id !== undefined ? l.source.id : l.source;
  const t = l.target.id !== undefined ? l.target.id : l.target;
  if (nodeIdx.has(s) && nodeIdx.has(t)) {
    resolvedLinks.push({source: s, target: t, type: l.type || 'related_to'});
  }
});

// --- FILTER STATE ---
let activeTypes = new Set(Object.keys(typeCounts));
let searchTerm = '';

// --- CONTROLS ---
const controls = d3.select('#controls');
const sortedTypes = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);
sortedTypes.forEach(([type, count]) => {
  controls.append('span')
    .attr('class', 'chip active')
    .attr('data-type', type)
    .html(`<span style="color:${color(type)}">\u25CF</span> ${type}<span class="count">${count}</span>`)
    .on('click', function() {
      const chip = d3.select(this);
      const t = chip.attr('data-type');
      if (activeTypes.has(t)) { activeTypes.delete(t); chip.classed('active', false); }
      else { activeTypes.add(t); chip.classed('active', true); }
      applyFilter();
    });
});

// --- SEARCH ---
d3.select('#search').on('input', function() {
  searchTerm = this.value.toLowerCase();
  applyFilter();
});

// --- SVG SETUP ---
const svg = d3.select('svg');
const width = window.innerWidth;
const height = window.innerHeight;
const g = svg.append('g');

// Zoom
const zoom = d3.zoom().scaleExtent([0.1, 8]).on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);

// --- SIMULATION ---
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(resolvedLinks).id(d => d.id).distance(40).strength(0.1))
  .force('charge', d3.forceManyBody().strength(-30).distanceMax(300))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(6))
  .alphaDecay(0.02);

// --- DRAW ---
const link = g.append('g').attr('class', 'links')
  .selectAll('line').data(resolvedLinks).enter().append('line')
  .attr('stroke', '#21262d').attr('stroke-width', 0.3).attr('stroke-opacity', 0.4);

const node = g.append('g').attr('class', 'nodes')
  .selectAll('circle').data(nodes).enter().append('circle')
  .attr('r', d => {
    if (d.type === 'module' || d.type === 'bounded_context' || d.type === 'layer') return 6;
    if (d.type === 'epic') return 5;
    return 3;
  })
  .attr('fill', d => color(d.type))
  .attr('stroke', '#0d1117').attr('stroke-width', 0.5)
  .call(drag(simulation));

// Tooltip
const tooltip = d3.select('#tooltip');
node.on('mouseover', (e, d) => {
  const content = (d.content || '').substring(0, 200);
  tooltip.select('.tt-id').text(d.id);
  tooltip.select('.tt-type').text(d.type + (d.source_file ? ' \u2022 ' + d.source_file : ''));
  tooltip.select('.tt-content').text(content);
  tooltip.style('display', 'block');
}).on('mousemove', e => {
  tooltip.style('left', (e.clientX + 14) + 'px').style('top', (e.clientY - 10) + 'px');
}).on('mouseout', () => { tooltip.style('display', 'none'); });

// Info
d3.select('#info').text(`${nodes.length} nodes \u2022 ${resolvedLinks.length} edges (${links.length < (graphData.links || graphData.edges || []).length ? 'sampled' : 'all'})`);

// Tick
simulation.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('cx', d => d.x).attr('cy', d => d.y);
});

// --- FILTER ---
function applyFilter() {
  node.attr('display', d => {
    const typeMatch = activeTypes.has(d.type);
    const searchMatch = !searchTerm || d.id.toLowerCase().includes(searchTerm) || (d.content || '').toLowerCase().includes(searchTerm);
    return (typeMatch && searchMatch) ? null : 'none';
  });
  const visibleIds = new Set();
  node.each(function(d) { if (d3.select(this).attr('display') !== 'none') visibleIds.add(d.id); });
  link.attr('display', d => {
    const sId = d.source.id !== undefined ? d.source.id : d.source;
    const tId = d.target.id !== undefined ? d.target.id : d.target;
    return (visibleIds.has(sId) && visibleIds.has(tId)) ? null : 'none';
  });
}

// --- DRAG ---
function drag(sim) {
  return d3.drag()
    .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
}
</script>
</body>
</html>"""


def generate_viz_html(
    index_path: Path,
    output_path: Path,
) -> Path:
    """Generate an interactive HTML visualization from the memory graph.

    Args:
        index_path: Path to the memory index.json file.
        output_path: Path to write the HTML file.

    Returns:
        The output path written to.
    """
    graph_data = json.loads(index_path.read_text())

    # Strip heavy content from nodes to keep the HTML small
    # Keep id, type, source_file, and first 200 chars of content
    slim_nodes = []
    for node in graph_data.get("nodes", []):
        slim_nodes.append({
            "id": node["id"],
            "type": node.get("type", "unknown"),
            "source_file": node.get("source_file", ""),
            "content": (node.get("content", "") or "")[:200],
        })

    # Build slim edge list
    links = graph_data.get("links", graph_data.get("edges", []))
    slim_links = []
    for link in links:
        slim_links.append({
            "source": link.get("source", ""),
            "target": link.get("target", ""),
            "type": link.get("type", link.get("relation", "related_to")),
        })

    slim_graph: dict[str, list[dict[str, str]]] = {
        "nodes": slim_nodes,
        "links": slim_links,
    }
    graph_json = json.dumps(slim_graph, separators=(",", ":"))

    html = _HTML_TEMPLATE.replace("%%GRAPH_DATA%%", graph_json)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    return output_path
