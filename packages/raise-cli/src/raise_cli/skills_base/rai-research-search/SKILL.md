---
name: rai-research-search
description: Execute searches across angles using Tavily, Brave, ddgr, and WebFetch. Scales by depth.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - WebFetch
  - Agent
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Search

## Purpose

Execute searches across all angles and extract findings. Scales from single-pass (quick) to multi-agent fan-out (standard/deep).

## Steps

### Step 1: Read Inputs

- Read `work/research/{topic}/frame.md` for depth and question
- If `scope.md` exists (standard/deep), read angles and queries
- If no scope (quick), derive 2-3 queries from the question directly

### Step 2: Execute Searches by Depth

**Quick (single-agent, inline):**
1. Run 2-3 `ddgr` queries + 1 Tavily query
2. WebFetch top 3-5 URLs
3. Extract key findings inline

**Standard/Deep (fan-out per angle):**
For each angle in scope.md, fork an agent:

```
Agent({
  subagent_type: "fork",
  prompt: "Research angle: {angle_name}. Execute these queries: {queries}.
    Tools: Use Bash for Tavily (curl to api.tavily.com with $TAVILY_API_KEY)
    and ddgr. Use WebFetch for top URLs.
    Return: JSON array of findings, each with {url, title, source_type, key_claim, evidence_level, excerpt}."
})
```

**Tavily API call pattern:**
```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "'$TAVILY_API_KEY'", "query": "{query}", "max_results": 5, "include_raw_content": false}'
```

**Brave Search API call pattern:**
```bash
curl -s "https://api.search.brave.com/res/v1/web/search?q={query}&count=5" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: $BRAVE_API_KEY"
```

### Step 3: Collect Raw Findings

Merge all findings into `work/research/{topic}/sources/raw-findings.md`:

```markdown
# Raw Findings: {topic}

## Angle: {angle_name}
### Source 1: {title}
- URL: {url}
- Type: {primary|secondary|tertiary}
- Evidence level: {Very High|High|Medium|Low}
- Key claim: {claim}
- Excerpt: {relevant excerpt}

...
```

### Step 4: Emit phase_result

```yaml
phase_result:
  status: done
  source_count: {N}
  angles_searched: {N or 1 for quick}
  artifacts:
    - work/research/{topic}/sources/raw-findings.md
```

## Output

| Item | Destination |
|------|-------------|
| Raw findings | `work/research/{topic}/sources/raw-findings.md` |
| Source count | phase_result → Evidence phase uses for dedup |
