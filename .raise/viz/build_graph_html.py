"""Build an interactive D3.js force-graph HTML from the RaiSE knowledge graph."""

import json
from pathlib import Path

INDEX = Path(".raise/rai/memory/index.json")
OUTPUT = Path(".raise/viz/graph.html")

# Node types to include (skip sessions, components, calibrations — too noisy)
INCLUDE_TYPES = {
    "module", "epic", "skill", "decision", "principle", "architecture",
    "layer", "bounded_context", "pattern", "guardrail", "artifact", "term", "story",
}

# Color palette per type
COLORS = {
    "module": "#4ecdc4",
    "epic": "#ff6b6b",
    "skill": "#ffe66d",
    "decision": "#a8e6cf",
    "principle": "#ff8b94",
    "architecture": "#dcedc1",
    "layer": "#ffd3b6",
    "bounded_context": "#d4a5a5",
    "pattern": "#9b59b6",
    "guardrail": "#3498db",
    "artifact": "#e67e22",
    "term": "#95a5a6",
    "story": "#e74c3c",
}

SIZE = {
    "module": 12, "layer": 11, "architecture": 11, "bounded_context": 10,
    "epic": 8, "skill": 7, "decision": 9, "principle": 7,
    "pattern": 5, "guardrail": 5, "artifact": 5, "term": 4, "story": 4,
}


def main() -> None:
    with open(INDEX) as f:
        data = json.load(f)

    # Filter nodes
    node_ids: set[str] = set()
    nodes: list[dict] = []
    for n in data["nodes"]:
        if n["type"] in INCLUDE_TYPES:
            node_ids.add(n["id"])
            label = n["id"].split("-", 1)[-1][:40] if "-" in n["id"] else n["id"][:40]
            nodes.append({
                "id": n["id"],
                "label": label,
                "type": n["type"],
                "color": COLORS.get(n["type"], "#999"),
                "size": SIZE.get(n["type"], 5),
                "content": (n.get("content") or "")[:200],
            })

    # Filter edges — only between included nodes, skip low-weight related_to
    edges: list[dict] = []
    seen_edges: set[tuple[str, str]] = set()
    for e in data["edges"]:
        s, t = e["source"], e["target"]
        if s not in node_ids or t not in node_ids:
            continue
        # For related_to, only keep weight >= 0.6
        if e["type"] == "related_to" and (e.get("weight") or 0) < 0.6:
            continue
        pair = (min(s, t), max(s, t))
        if pair in seen_edges:
            continue
        seen_edges.add(pair)
        edges.append({"source": s, "target": t, "type": e["type"], "weight": e.get("weight", 0.5)})

    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

    graph_data = json.dumps({"nodes": nodes, "links": edges})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>RaiSE Knowledge Graph</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #1a1a2e; color: #eee; font-family: 'Segoe UI', system-ui, sans-serif; overflow: hidden; }}
  #info {{
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(26,26,46,0.92); border: 1px solid #333; border-radius: 8px;
    padding: 16px; max-width: 360px; font-size: 13px; line-height: 1.5;
  }}
  #info h1 {{ font-size: 18px; margin-bottom: 8px; color: #4ecdc4; }}
  #info .stats {{ color: #888; margin-bottom: 10px; }}
  #legend {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
  .legend-item {{ display: flex; align-items: center; gap: 4px; font-size: 11px; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  #tooltip {{
    position: fixed; display: none; background: rgba(26,26,46,0.95);
    border: 1px solid #4ecdc4; border-radius: 6px; padding: 10px;
    font-size: 12px; max-width: 300px; z-index: 20; pointer-events: none;
  }}
  #tooltip .tt-type {{ color: #4ecdc4; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}
  #tooltip .tt-id {{ font-weight: bold; margin: 4px 0; }}
  #tooltip .tt-content {{ color: #aaa; font-size: 11px; }}
  #controls {{
    position: fixed; bottom: 16px; left: 16px; z-index: 10;
    display: flex; gap: 8px;
  }}
  #controls button {{
    background: #16213e; border: 1px solid #444; color: #eee;
    padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12px;
  }}
  #controls button:hover {{ background: #1a1a4e; border-color: #4ecdc4; }}
  #filter-panel {{
    position: fixed; top: 16px; right: 16px; z-index: 10;
    background: rgba(26,26,46,0.92); border: 1px solid #333; border-radius: 8px;
    padding: 12px; font-size: 12px;
  }}
  #filter-panel label {{ display: block; margin: 3px 0; cursor: pointer; }}
  #filter-panel input {{ margin-right: 6px; }}
</style>
</head>
<body>
<div id="info">
  <h1>RaiSE Knowledge Graph</h1>
  <div class="stats">{len(nodes)} nodes &middot; {len(edges)} edges</div>
  <div>Drag nodes &middot; Scroll to zoom &middot; Hover for details</div>
  <div id="legend"></div>
</div>
<div id="tooltip">
  <div class="tt-type"></div>
  <div class="tt-id"></div>
  <div class="tt-content"></div>
</div>
<div id="filter-panel"></div>
<div id="controls">
  <button onclick="resetZoom()">Reset Zoom</button>
  <button onclick="toggleLabels()">Toggle Labels</button>
</div>
<svg id="graph"></svg>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data = {graph_data};
const width = window.innerWidth;
const height = window.innerHeight;
let showLabels = true;

const svg = d3.select("#graph").attr("width", width).attr("height", height);
const g = svg.append("g");

// Zoom
const zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", (e) => g.attr("transform", e.transform));
svg.call(zoom);
function resetZoom() {{ svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity); }}

// Type sets for filtering
const types = [...new Set(data.nodes.map(n => n.type))].sort();
const activeTypes = new Set(types);

// Legend
const legend = d3.select("#legend");
const colors = {json.dumps(COLORS)};
types.forEach(t => {{
  legend.append("div").attr("class","legend-item").html(
    `<div class="legend-dot" style="background:${{colors[t]||'#999'}}"></div>${{t}}`
  );
}});

// Filter panel
const fp = d3.select("#filter-panel");
fp.append("div").style("font-weight","bold").style("margin-bottom","6px").text("Filter Types");
types.forEach(t => {{
  const count = data.nodes.filter(n => n.type === t).length;
  const lbl = fp.append("label");
  lbl.append("input").attr("type","checkbox").attr("checked",true)
    .on("change", function() {{
      if (this.checked) activeTypes.add(t); else activeTypes.delete(t);
      updateVisibility();
    }});
  lbl.append("span").text(`${{t}} (${{count}})`);
}});

// Simulation
const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(80).strength(0.3))
  .force("charge", d3.forceManyBody().strength(-120))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide().radius(d => d.size + 2));

// Edges
const link = g.append("g").selectAll("line").data(data.links).join("line")
  .attr("stroke", "#ffffff10").attr("stroke-width", d => Math.max(0.5, d.weight * 2));

// Nodes
const node = g.append("g").selectAll("circle").data(data.nodes).join("circle")
  .attr("r", d => d.size).attr("fill", d => d.color).attr("stroke", "#fff").attr("stroke-width", 0.5)
  .style("cursor", "pointer")
  .call(d3.drag().on("start", dragStart).on("drag", dragged).on("end", dragEnd));

// Labels
const label = g.append("g").selectAll("text").data(data.nodes).join("text")
  .text(d => d.label).attr("font-size", d => Math.max(8, d.size * 0.8))
  .attr("fill", "#ccc").attr("dx", d => d.size + 3).attr("dy", 3)
  .style("pointer-events", "none");

// Tooltip
const tooltip = d3.select("#tooltip");
node.on("mouseover", (e, d) => {{
  tooltip.style("display","block")
    .style("left", (e.clientX+12)+"px").style("top", (e.clientY+12)+"px");
  tooltip.select(".tt-type").text(d.type);
  tooltip.select(".tt-id").text(d.id);
  tooltip.select(".tt-content").text(d.content || "");
  // Highlight connections
  const connected = new Set();
  data.links.forEach(l => {{
    const sid = typeof l.source === "object" ? l.source.id : l.source;
    const tid = typeof l.target === "object" ? l.target.id : l.target;
    if (sid === d.id) connected.add(tid);
    if (tid === d.id) connected.add(sid);
  }});
  node.attr("opacity", n => n.id === d.id || connected.has(n.id) ? 1 : 0.15);
  link.attr("opacity", l => {{
    const sid = typeof l.source === "object" ? l.source.id : l.source;
    const tid = typeof l.target === "object" ? l.target.id : l.target;
    return sid === d.id || tid === d.id ? 0.8 : 0.03;
  }});
  label.attr("opacity", n => n.id === d.id || connected.has(n.id) ? 1 : 0.1);
}}).on("mouseout", () => {{
  tooltip.style("display","none");
  node.attr("opacity", 1); link.attr("opacity", 1); label.attr("opacity", 1);
}});

simulation.on("tick", () => {{
  link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("cx",d=>d.x).attr("cy",d=>d.y);
  label.attr("x",d=>d.x).attr("y",d=>d.y);
}});

function dragStart(e,d) {{ if(!e.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }}
function dragged(e,d) {{ d.fx=e.x; d.fy=e.y; }}
function dragEnd(e,d) {{ if(!e.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; }}

function toggleLabels() {{
  showLabels = !showLabels;
  label.style("display", showLabels ? "block" : "none");
}}

function updateVisibility() {{
  node.style("display", d => activeTypes.has(d.type) ? "block" : "none");
  label.style("display", d => showLabels && activeTypes.has(d.type) ? "block" : "none");
  link.style("display", l => {{
    const sid = typeof l.source === "object" ? l.source.id : l.source;
    const tid = typeof l.target === "object" ? l.target.id : l.target;
    const sn = data.nodes.find(n => n.id === sid);
    const tn = data.nodes.find(n => n.id === tid);
    return sn && tn && activeTypes.has(sn.type) && activeTypes.has(tn.type) ? "block" : "none";
  }});
}}
</script>
</body>
</html>"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html)
    print(f"✓ Written to {OUTPUT}")


if __name__ == "__main__":
    main()
