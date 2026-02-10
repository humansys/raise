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
  #tooltip .tt-tags { font-size: 10px; color: #7c3aed; margin-bottom: 6px; }
  #tooltip .tt-from { font-size: 10px; color: #d29922; margin-bottom: 6px; }
  #tooltip .tt-content { color: #c9d1d9; line-height: 1.4; max-height: 200px; overflow: hidden; white-space: pre-wrap; }
  #search { position: fixed; top: 12px; right: 12px; z-index: 10; padding: 6px 12px; border-radius: 8px; border: 1px solid #30363d; background: #161b22; color: #c9d1d9; font-size: 13px; width: 220px; outline: none; }
  #search:focus { border-color: #58a6ff; }
  #search::placeholder { color: #484f58; }
  svg { width: 100vw; height: 100vh; }
</style>
</head>
<body>
<div id="controls"></div>
<input id="search" type="text" placeholder="Search nodes..." />
<div id="tooltip"><div class="tt-id"></div><div class="tt-type"></div><div class="tt-tags"></div><div class="tt-from"></div><div class="tt-content"></div></div>
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

// --- DOMAIN CLUSTERS ---
// Map each node type to a high-level domain
const typeToDomain = {
  principle: 'Governance', guardrail: 'Governance', requirement: 'Governance', outcome: 'Governance', term: 'Governance',
  component: 'Architecture', module: 'Architecture', bounded_context: 'Architecture', layer: 'Architecture', architecture: 'Architecture',
  pattern: 'Memory', calibration: 'Memory', session: 'Memory',
  epic: 'Work', story: 'Work', decision: 'Work', project: 'Work',
  skill: 'Skills'
};
const domainList = ['Governance', 'Architecture', 'Memory', 'Work', 'Skills'];
const domainColors = {
  Governance: '#f778ba', Architecture: '#3fb950', Memory: '#a371f7', Work: '#58a6ff', Skills: '#79c0ff'
};
function getDomain(type) { return typeToDomain[type] || 'Other'; }

// --- PATTERN SUB-CATEGORIES ---
// Top pattern categories with distinct colors for visual separation
const patternCatColors = {
  architecture: '#c9b1ff', process: '#d2a8ff', testing: '#b088f9',
  design: '#a371f7', graph: '#8957e5', skills: '#6e40c9',
  cli: '#9d86e9', discovery: '#bf8cff', ontology: '#7c3aed',
  workflow: '#e0c3fc', governance: '#dbb7ff', validation: '#cab0f5',
  research: '#a78bfa', memory: '#8b5cf6', general: '#7e6cb5'
};
function patternColor(category) { return patternCatColors[category] || '#a371f7'; }

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

// --- NODE RADIUS ---
function nodeRadius(d) {
  if (d.type === 'module' || d.type === 'bounded_context' || d.type === 'layer') return 18;
  if (d.type === 'epic' || d.type === 'architecture') return 15;
  if (d.type === 'story' || d.type === 'skill' || d.type === 'principle') return 12;
  return 9;
}

// --- CLUSTER LAYOUT ---
// Position domains in a circle around center
const clusterRadius = Math.min(width, height) * 0.3;
const domainCenters = {};
domainList.forEach((d, i) => {
  const angle = (i / domainList.length) * 2 * Math.PI - Math.PI / 2;
  domainCenters[d] = { x: width / 2 + clusterRadius * Math.cos(angle), y: height / 2 + clusterRadius * Math.sin(angle) };
});
domainCenters['Other'] = { x: width / 2, y: height / 2 };

// --- PATTERN SUB-CLUSTER POSITIONS ---
// Collect unique pattern categories and arrange them in a mini-circle within Memory domain
const patternCategories = [...new Set(nodes.filter(n => n.type === 'pattern').map(n => n.category || 'general'))];
const memCenter = domainCenters['Memory'];
const subRadius = clusterRadius * 0.4;
const patternCenters = {};
patternCategories.forEach((cat, i) => {
  const angle = (i / patternCategories.length) * 2 * Math.PI - Math.PI / 2;
  patternCenters[cat] = { x: memCenter.x + subRadius * Math.cos(angle), y: memCenter.y + subRadius * Math.sin(angle) };
});

// Target position for each node — patterns get sub-cluster positions
function targetX(d) {
  if (d.type === 'pattern') return patternCenters[d.category || 'general']?.x || memCenter.x;
  return domainCenters[getDomain(d.type)]?.x || width / 2;
}
function targetY(d) {
  if (d.type === 'pattern') return patternCenters[d.category || 'general']?.y || memCenter.y;
  return domainCenters[getDomain(d.type)]?.y || height / 2;
}

// --- SIMULATION ---
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(resolvedLinks).id(d => d.id).distance(60).strength(0.05))
  .force('charge', d3.forceManyBody().strength(-40).distanceMax(400))
  .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 3))
  .force('x', d3.forceX(d => targetX(d)).strength(0.15))
  .force('y', d3.forceY(d => targetY(d)).strength(0.15))
  .alphaDecay(0.02);

// --- DRAW ---
// Domain background labels
const domainLabels = g.append('g').attr('class', 'domain-labels');
domainList.forEach(d => {
  const c = domainCenters[d];
  domainLabels.append('text')
    .attr('x', c.x).attr('y', c.y - clusterRadius * 0.35)
    .attr('text-anchor', 'middle').attr('font-size', '18px').attr('font-weight', '600')
    .attr('fill', domainColors[d] || '#484f58').attr('opacity', 0.25)
    .text(d.toUpperCase());
});

// Pattern sub-cluster labels
patternCategories.forEach(cat => {
  const c = patternCenters[cat];
  if (c) {
    domainLabels.append('text')
      .attr('x', c.x).attr('y', c.y - subRadius * 0.25)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('font-weight', '500')
      .attr('fill', patternColor(cat)).attr('opacity', 0.35)
      .text(cat);
  }
});

// Edge lines
const link = g.append('g').attr('class', 'links')
  .selectAll('line').data(resolvedLinks).enter().append('line')
  .attr('stroke', '#21262d').attr('stroke-width', 0.5).attr('stroke-opacity', 0.35);

// Edge labels (shown on hover via CSS)
const linkLabel = g.append('g').attr('class', 'link-labels')
  .selectAll('text').data(resolvedLinks).enter().append('text')
  .text(d => d.type.replace(/_/g, ' '))
  .attr('font-size', '7px').attr('fill', '#484f58').attr('text-anchor', 'middle')
  .attr('dy', -3).style('pointer-events', 'none').attr('opacity', 0);

// Node groups (circle + label)
const nodeG = g.append('g').attr('class', 'nodes')
  .selectAll('g').data(nodes).enter().append('g')
  .call(drag(simulation));

nodeG.append('circle')
  .attr('r', d => nodeRadius(d))
  .attr('fill', d => d.type === 'pattern' ? patternColor(d.category || 'general') : color(d.type))
  .attr('stroke', '#0d1117').attr('stroke-width', 1);

// Node labels
nodeG.append('text')
  .text(d => d.id.length > 20 ? d.id.substring(0, 18) + '..' : d.id)
  .attr('font-size', d => nodeRadius(d) > 12 ? '8px' : '6px')
  .attr('fill', '#c9d1d9')
  .attr('text-anchor', 'middle')
  .attr('dy', d => nodeRadius(d) + 10)
  .style('pointer-events', 'none');

// Tooltip
const tooltip = d3.select('#tooltip');
nodeG.on('mouseover', (e, d) => {
  tooltip.select('.tt-id').text(d.id);
  if (d.type === 'pattern') {
    tooltip.select('.tt-type').text('pattern \u2022 ' + (d.category || 'general'));
    tooltip.select('.tt-tags').text(d.tags && d.tags.length ? 'Tags: ' + d.tags.join(', ') : '');
    tooltip.select('.tt-from').text(d.learned_from ? 'Learned from: ' + d.learned_from : '');
    tooltip.select('.tt-content').text(d.content || '');
  } else {
    tooltip.select('.tt-type').text(d.type + (d.source_file ? ' \u2022 ' + d.source_file : ''));
    tooltip.select('.tt-tags').text('');
    tooltip.select('.tt-from').text('');
    tooltip.select('.tt-content').text((d.content || '').substring(0, 200));
  }
  tooltip.style('display', 'block');
  // Show edge labels for connected edges
  linkLabel.attr('opacity', l => {
    const sId = l.source.id !== undefined ? l.source.id : l.source;
    const tId = l.target.id !== undefined ? l.target.id : l.target;
    return (sId === d.id || tId === d.id) ? 0.8 : 0;
  });
  link.attr('stroke', l => {
    const sId = l.source.id !== undefined ? l.source.id : l.source;
    const tId = l.target.id !== undefined ? l.target.id : l.target;
    return (sId === d.id || tId === d.id) ? '#58a6ff' : '#21262d';
  }).attr('stroke-width', l => {
    const sId = l.source.id !== undefined ? l.source.id : l.source;
    const tId = l.target.id !== undefined ? l.target.id : l.target;
    return (sId === d.id || tId === d.id) ? 1.5 : 0.5;
  });
}).on('mousemove', e => {
  tooltip.style('left', (e.clientX + 14) + 'px').style('top', (e.clientY - 10) + 'px');
}).on('mouseout', () => {
  tooltip.style('display', 'none');
  linkLabel.attr('opacity', 0);
  link.attr('stroke', '#21262d').attr('stroke-width', 0.5);
});

// Info
d3.select('#info').text(`${nodes.length} nodes \u2022 ${resolvedLinks.length} edges (${links.length < (graphData.links || graphData.edges || []).length ? 'sampled' : 'all'})`);

// Tick
simulation.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  linkLabel.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2);
  nodeG.attr('transform', d => `translate(${d.x},${d.y})`);
});

// --- FILTER ---
function applyFilter() {
  nodeG.attr('display', d => {
    const typeMatch = activeTypes.has(d.type);
    const searchMatch = !searchTerm || d.id.toLowerCase().includes(searchTerm) || (d.content || '').toLowerCase().includes(searchTerm);
    return (typeMatch && searchMatch) ? null : 'none';
  });
  const visibleIds = new Set();
  nodeG.each(function(d) { if (d3.select(this).attr('display') !== 'none') visibleIds.add(d.id); });
  link.attr('display', d => {
    const sId = d.source.id !== undefined ? d.source.id : d.source;
    const tId = d.target.id !== undefined ? d.target.id : d.target;
    return (visibleIds.has(sId) && visibleIds.has(tId)) ? null : 'none';
  });
  linkLabel.attr('display', d => {
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
    # For patterns: keep full content + context tags for sub-clustering
    # For others: keep first 200 chars
    slim_nodes = []
    for node in graph_data.get("nodes", []):
        meta: dict[str, object] = node.get("metadata") or {}
        is_pattern = node.get("type") == "pattern"
        content_raw: str = node.get("content", "") or ""
        slim_node: dict[str, str | list[str]] = {
            "id": node["id"],
            "type": node.get("type", "unknown"),
            "source_file": node.get("source_file", ""),
            "content": content_raw if is_pattern else content_raw[:200],
        }
        if is_pattern:
            ctx: list[str] = meta.get("context") or []  # type: ignore[assignment]
            slim_node["category"] = ctx[0] if ctx else "general"
            slim_node["tags"] = ctx
            slim_node["learned_from"] = str(meta.get("learned_from", ""))
        slim_nodes.append(slim_node)

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
