# Research: Multi-Instance Jira Configuration

> Quick-scan research for S494.4 design decision
> Date: 2026-03-19

## Question
How do mature open source tools that integrate with Jira handle multi-instance configuration?

## Files
- `multi-instance-jira-report.md` — Pattern synthesis and recommendation
- `sources/evidence-catalog.md` — Per-tool evidence with sources and confidence levels

## Tools Analyzed (7)
1. jira-cli (5.3k stars) — multiple config files, flag switching
2. python-jira (2.1k stars) — multiple client instances, programmatic
3. go-jira (2.7k stars) — directory-hierarchy config merging
4. terraform-provider-jira (183 stars) — provider aliases
5. Backstage Jira Dashboard (40 stars) — named instances array + annotation routing
6. Jenkins Jira Plugin — UI-registered sites + site parameter
7. Appfire ACLI — named aliases + regex matching

## Key Convergences
1. **Named instances** (4/7 tools) — strongest config pattern
2. **Explicit routing** (7/7 tools) — no tool uses auto-discovery
3. **Per-instance auth** (7/7 tools) — no global state mutation

## Recommendation Summary
- `instances:` array with named entries (name, url, auth env vars)
- `projects:` mapping for explicit project-to-instance routing
- `default: true` flag on one instance for fallback
- Backward-compatible with single-instance configs
