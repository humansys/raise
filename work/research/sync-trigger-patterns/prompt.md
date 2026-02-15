# Research Prompt: Sync Trigger Patterns

## Role

You are a distributed systems research specialist investigating synchronization trigger mechanisms used in production engineering tools.

## Research Question

**Primary:** When and how do engineering tools (project management, build systems, CI/CD, issue trackers) trigger synchronization between systems?

**Secondary:**
- What are the architectural patterns for sync triggers (manual, event-driven, scheduled, hybrid)?
- What are the latency vs reliability tradeoffs for each pattern?
- How do production systems handle sync failures, retries, and eventual consistency?
- What hybrid approaches combine multiple trigger mechanisms?

## Search Strategy

### Keywords
- "webhook vs polling architecture"
- "event-driven synchronization patterns"
- "sync trigger mechanisms distributed systems"
- "GitHub Jira integration sync patterns"
- "bidirectional sync failure handling"
- "eventual consistency retry strategies"
- "hybrid push pull synchronization"
- "linear app sync architecture"
- "slack api event subscriptions"

### Source Priorities
1. Official documentation from tools with mature sync (GitHub, Jira, Linear, Slack)
2. Engineering blogs from companies building integration platforms (Zapier, n8n, Airbyte)
3. Academic papers on distributed synchronization
4. Open source integration tools (Meltano, Airbyte, webhooks libraries)
5. Community discussions on sync reliability patterns

## Evidence Evaluation

**Very High:**
- Official API documentation from GitHub, Atlassian, Linear
- Production architecture blogs from integration platforms
- Peer-reviewed distributed systems papers

**High:**
- Engineering blogs from companies with proven integrations
- Popular open source sync frameworks (>1k stars)

**Medium:**
- Conference talks on integration patterns
- Community-validated approaches (>100 upvotes)

**Low:**
- Single-source blog posts
- Unvalidated approaches

## Output Requirements

### Evidence Catalog
For each source:
- Title and URL
- Evidence level (Very High/High/Medium/Low)
- Key finding (one-line)
- Relevance to RaiSE backlog sync

### Triangulated Findings
Each major claim must have 3+ independent sources. Document:
- Sync trigger patterns (manual, event, scheduled, hybrid)
- Latency characteristics for each pattern
- Reliability characteristics and failure modes
- Retry strategies and backoff patterns
- Hybrid approaches that combine patterns

### Synthesis
- Pattern convergence: What do mature tools agree on?
- Tradeoff matrix: Latency vs reliability for each pattern
- Failure handling: Common retry strategies
- Gaps: What's context-specific to RaiSE?

### Recommendation
- Actionable sync trigger design for RaiSE
- Confidence level (HIGH/MEDIUM/LOW)
- Trade-offs and risks
- Implementation approach

## Quality Checklist
- [ ] 10+ sources (scaled to importance)
- [ ] Major claims triangulated (3+ sources)
- [ ] Evidence levels assigned
- [ ] Contrary evidence acknowledged
- [ ] Recommendation traces to findings
- [ ] Confidence level explicit

## Context

RaiSE is designing backlog synchronization between:
- Local unified graph (raise memory)
- External issue trackers (Jira, Linear, GitHub Issues)

Key considerations:
- Epic lifecycle events (start, close) as natural sync points
- Manual commands for user control
- Reliability over latency (eventual consistency acceptable)
- Failure handling without data loss
- Simple implementation over complex event infrastructure
