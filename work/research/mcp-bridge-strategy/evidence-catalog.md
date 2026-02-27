# Evidence Catalog: MCP Bridge Strategy for E301

> **Research:** SES-298 (2026-02-27)
> **Trigger:** Epic E301 architecture pivot — evaluate MCPorter vs alternatives
> **Method:** 4 parallel research streams, 14+ sources triangulated

## Sources

| # | Source | Type | Reputation | URL |
|---|--------|------|------------|-----|
| S1 | MCP Python SDK (v1.26.0) | Official SDK | Very High | https://github.com/modelcontextprotocol/python-sdk |
| S2 | FastMCP Client (23K stars) | OSS library | Very High | https://github.com/PrefectHQ/fastmcp |
| S3 | MCPorter (2.2K stars) | OSS CLI tool | High | https://github.com/steipete/mcporter |
| S4 | mcp-atlassian (sooperset) | OSS MCP server | High | https://github.com/sooperset/mcp-atlassian |
| S5 | atlassian-python-api | OSS library | Very High | https://pypi.org/project/atlassian-python-api/ |
| S6 | Anthropic engineering blog | Official blog | Very High | https://www.anthropic.com/engineering/code-execution-with-mcp |
| S7 | Sentry CTO (David Cramer) | Practitioner blog | Very High | https://cra.mr/subagents-with-mcp/ |
| S8 | Manus system prompts (leaked) | Primary source | High | https://gist.github.com/jlia0/db0a9695b3ca7609c9b1a08dcbf872c9 |
| S9 | Manus official blog | Official blog | Very High | https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus |
| S10 | philschmid/mcp-cli | OSS CLI tool | High | https://github.com/philschmid/mcp-cli |
| S11 | MetaMCP (2.1K stars) | OSS aggregator | High | https://github.com/metatool-ai/metamcp |
| S12 | MCP Gateway Registry | OSS governance | Medium | https://github.com/agentic-community/mcp-gateway-registry |
| S13 | Runlayer | Commercial product | Medium | https://www.runlayer.com/ |
| S14 | LlamaIndex blog | Practitioner blog | High | https://www.llamaindex.ai/blog/skills-vs-mcp-tools-for-agents-when-to-use-what |
| S15 | OpenTelemetry agent blog | Official blog | Very High | https://opentelemetry.io/blog/2025/ai-agent-observability/ |
| S16 | Sentry CTO context mgmt | Practitioner blog | Very High | https://cra.mr/context-management-and-mcp/ |

## Key Findings

### F1: MCP Python SDK has a full programmatic client (S1)

The official `mcp` Python package (v1.26.0, stable) provides `ClientSession.call_tool()`:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(command="mcp-atlassian")) as (r, w):
    async with ClientSession(r, w) as session:
        await session.initialize()
        result = await session.call_tool("jira_get_issue", {"issue_key": "RAISE-301"})
```

Supports stdio, SSE, and Streamable HTTP transports. No CLI for tool calling — library only.
**Confidence:** Very High (official SDK, 21K stars, Python 3.10+)

### F2: FastMCP Client is the most mature Python MCP client (S2)

23K stars, Prefect-maintained. In-process calling (no network):

```python
from fastmcp import Client
client = Client(server)  # can be in-process, stdio, or HTTP
async with client:
    result = await client.call_tool("jira_get_issue", {"issue_key": "RAISE-301"})
```

**Confidence:** Very High

### F3: mcp-atlassian wraps atlassian-python-api (S4, S5)

The MCP server we use (`mcp-atlassian`, 65 tools) has this architecture:
```
MCP tool layer (thin) → JiraFetcher (20 mixins) → atlassian-python-api → Jira REST API
```

The `atlassian-python-api` is the actual documented, stable library underneath.
Importing `JiraFetcher` directly is possible but undocumented/unstable API.
**Confidence:** High

### F4: MCPorter requires Node.js — Python alternatives exist (S3, S1, S2)

MCPorter is TypeScript/Node.js only. Python-native options:
- Official MCP SDK client (library, no CLI)
- FastMCP Client (library, no CLI)
- `cli-mcp` on PyPI (CLI, but low visibility/trust)
- IBM/mcp-cli (Python, but heavy/overkill)

**No mature Python CLI equivalent to MCPorter exists.** The Python path is library-based.
**Confidence:** High

### F5: Anthropic recommends filesystem-based thin wrappers (S6)

Anthropic's own pattern: wrap each MCP tool as a thin function in `./servers/{name}/toolName.ts`. Agent discovers by listing filesystem, reads only what it needs, writes code that calls them. **98.7% token reduction** (150K → 2K).
**Confidence:** Very High (Anthropic official engineering blog)

### F6: Sentry subagent pattern bundles MCP tools (S7)

Wrap all domain MCP tools behind a single subagent tool. Parent agent sees 1 tool (~720 tokens) instead of full suite (~14K). **95% reduction.** Trade-off: ~2x latency.
**Confidence:** Very High (Sentry CTO, open source implementation)

### F7: Manus uses CLI subprocess, not SDK (S8, S9)

Manus wraps MCP tools as shell commands in an Ubuntu sandbox. Agent generates one tool call per iteration. Uses state machine to mask (not remove) tools per state, preserving KV-cache.
**Confidence:** High

### F8: No RaiSE-equivalent exists for developer governance + MCP abstraction (S13, S12)

Runlayer is closest commercial competitor but targets enterprise IT (registry, approval workflows, SSO). Not developer-centric. No framework combines: (a) developer workflow governance, (b) MCP tool abstraction, (c) telemetry/observability.
**Confidence:** High

### F9: OTel semantic conventions for agent observability are emerging (S15)

OpenTelemetry developing semantic conventions for agent tracing. Arize AI Phoenix (open source, OTel + OpenInference) is de facto standard.
**Confidence:** High

### F10: Counter-evidence — skills not always better than MCP (S14, S16)

LlamaIndex found MCP-based docs tools outperformed skill-based instructions. Cramer argues quality of tool descriptions matters more than quantity reduction. "Spend more to save more."
**Confidence:** High

## Strategic Options for E301

### Option A: MCPorter (subprocess → Node.js CLI → MCP server)
- **Pro:** Ready-made CLI, `--json` output, zero Python code for bridge
- **Con:** Node.js/npx dependency, subprocess overhead, not Python-native
- **Effort:** S301.3 = M (mapping layer only)
- **Evidence:** S3, S8 (Manus validates subprocess pattern)

### Option B: MCP Python SDK Client (async Python → stdio/HTTP → MCP server)
- **Pro:** Pure Python, official SDK, full transport support, async-native
- **Con:** Session management boilerplate, async complexity in sync CLI context
- **Effort:** S301.3 = M (bridge ~100 LOC + mapping layer)
- **Evidence:** S1, S2

### Option C: FastMCP Client (Python → in-process or stdio → MCP server)
- **Pro:** Simplest API, in-process option, Prefect-maintained, 23K stars
- **Con:** Additional dependency (fastmcp), may overlap with official SDK
- **Effort:** S301.3 = S-M
- **Evidence:** S2

### Option D: atlassian-python-api directly (Python → REST API)
- **Pro:** Stable documented API, no MCP indirection, simplest dependency chain
- **Con:** Jira/Confluence specific (not generic bridge), must handle auth/pagination
- **Effort:** S301.3 = M (but no reusable bridge for other MCP servers)
- **Evidence:** S4, S5

### Option E: Hybrid — MCP SDK bridge + direct fallback
- **Pro:** Generic bridge (reusable for any MCP) + can fall back to direct API
- **Con:** Two code paths to maintain
- **Effort:** S301.3 = M-L
- **Evidence:** S1, S5

## Recommendation

**Option B (MCP Python SDK Client)** is the strongest choice:
1. Pure Python — no Node.js dependency
2. Official SDK — highest stability/support guarantee
3. Generic — works with ANY MCP server, not just Atlassian
4. Async-native — aligns with existing async protocols in S301.1
5. The "bridge" is ~100 lines of Python wrapping ClientSession
6. Reusable for S301.5 (Confluence) and future adapters

MCPorter (Option A) was our initial enthusiasm, but the research shows it adds an unnecessary
Node.js dependency when a mature Python SDK exists for the same purpose.

## Contrary Evidence

- F10 suggests skills don't always outperform MCP tools (LlamaIndex finding)
- F5/F6 suggest even more radical approaches (filesystem wrappers, subagents) that we're not considering yet
- Cramer (S16) argues against "progressive disclosure" — maybe we should keep MCP tools available AND add CLI abstraction rather than replacing one with the other

## Open Questions

1. Should the bridge support both stdio and HTTP transports? (stdio for local MCP servers, HTTP for remote)
2. Should we align telemetry with OTel semantic conventions from the start? (F9)
3. Is the async complexity worth it for CLI context? (S301.1 already has _run_sync() helper)
4. Should we consider the Anthropic filesystem-wrapper pattern (F5) as a Phase 2 enhancement?
