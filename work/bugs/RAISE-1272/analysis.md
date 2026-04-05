# RAISE-1272: Analysis

## Method: Direct (XS — cause evident from code)

Error path:
1. `/rai-adapter-setup` calls `suggest_routing(tree)` with top-level pages
2. Top-level pages include both containers ("Architecture") and artifacts ("ADR-041: Skill Runtime Orchestration")
3. `_ROUTING_KEYWORDS["adr"]` includes `"adr"` as a keyword
4. Line 111: `if keyword in title_lower` — "adr" is a substring of "adr-041: skill runtime orchestration"
5. First match wins (line 108-109: `if artifact_type in suggestions: continue`)
6. If the artifact page appears before the container page in tree.children, wrong page is selected

## Root Cause

Substring matching (`keyword in title_lower`) cannot distinguish container pages from individual artifact pages. The keyword "adr" matches both "Architecture Decision Records" and "ADR-041: Skill Runtime...". Iteration order determines which wins.

## Fix Approach

Add an artifact-title filter: skip pages whose titles match the pattern `WORD-NNN:` (e.g., "ADR-041:", "RAISE-123:") — these are individual artifacts, not containers. This is simple, targeted, and handles the real-world case without over-engineering.

Additionally, if multiple candidates match the same artifact type, prefer the shorter title (container pages tend to have short generic names).
