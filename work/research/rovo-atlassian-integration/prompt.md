# Research Prompt: Rovo AI & Atlassian Integration Strategy

## Research ID
RES-ROVO-001

## Context

**Decision to inform:** E8 Work Tracking Graph design — ensure parsers, models, and relationships are compatible with future Atlassian ecosystem integration (V3).

**Deadline context:** Mar 14, 2026 Rovo AI webinar — need integration strategy before then.

**Depth:** Standard (4-8h equivalent, but AI-assisted = ~1h)

## Primary Questions

1. **What is Rovo AI?** — Architecture, capabilities, integration points, APIs
2. **What is the Teamwork Graph?** — Entity types, relationships, how it connects Atlassian products
3. **How do third-party tools integrate?** — Forge apps, Connect apps, REST APIs, GraphQL
4. **What patterns exist for bidirectional sync?** — Jira ↔ external systems

## Secondary Questions

- What entity types does Jira expose? (Epic, Story, Task, Bug, etc.)
- What metadata is available? (status, assignee, sprint, custom fields)
- How do Confluence and Jira link? (page ↔ issue relationships)
- What are Rovo Agents? How do they interact with the graph?
- What's the authentication model? (OAuth, API tokens, Forge)

## Search Strategy

### Keywords
- "Rovo AI platform" "Atlassian Rovo"
- "Teamwork Graph Atlassian" "knowledge graph Jira Confluence"
- "Atlassian Forge" "Atlassian Connect"
- "Jira REST API" "Jira GraphQL"
- "Rovo agents" "Rovo dev"
- "Atlassian AI" "Atlassian intelligence"

### Source Priority
1. Official Atlassian documentation (developer.atlassian.com)
2. Atlassian engineering blog
3. Forge/Connect app documentation
4. Community forums (Atlassian Community)
5. Conference talks (Team, Atlassian Summit)

## Output Requirements

1. **Evidence catalog** with source ratings
2. **Entity mapping** — Atlassian types → RaiSE concepts
3. **Integration architecture draft** — how Work Graph connects
4. **Recommendations** for E8 design decisions

## Quality Checklist

- [ ] 10+ sources consulted
- [ ] Official docs prioritized
- [ ] Claims triangulated where possible
- [ ] Gaps/unknowns documented
- [ ] Actionable for E8 design
