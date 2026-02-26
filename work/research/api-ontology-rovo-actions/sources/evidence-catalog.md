# Evidence Catalog: Rovo Agent Action Design

## Sources

### S1 — Forge Action Module Reference
- **URL**: https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/
- **Type**: Official documentation
- **Evidence Level**: Very High
- **Key Findings**:
  - Action manifest schema: key, name, function/endpoint, actionVerb, description, inputs
  - actionVerb is mandatory: `GET`, `CREATE`, `UPDATE`, `DELETE`, `TRIGGER`
  - Input types limited to: `string`, `integer`, `number`, `boolean`
  - Description is what the LLM reads to decide when to invoke — critical for AI routing
  - 5 MB data limit per action invocation
  - CREATE/UPDATE/DELETE/TRIGGER verbs won't fire from automation rules
  - Security: never trust input values for auth; read accountId from context
  - Return value: any string or JSON, agent converts to natural language

### S2 — Forge Rovo Agent Module Reference
- **URL**: https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/
- **Type**: Official documentation
- **Evidence Level**: Very High
- **Key Findings**:
  - Agent name max 30 characters
  - Prompt is the primary behavior control mechanism
  - Actions referenced by key in agent manifest
  - Prompt can be inline YAML or external resource file
  - Prompt structure: role definition, capabilities list, action execution steps, output format
  - Use `---` delimiters to separate instruction sections
  - conversationStarters guide users on what agent can do
  - followUpPrompt generates post-response suggestions

### S3 — External APIs + Rovo Agents: What Actually Works (Community)
- **URL**: https://community.atlassian.com/forums/Atlassian-AI-Rovo-articles/External-APIs-Rovo-Agents-What-Actually-Works/ba-p/3096718
- **Type**: Community post (practitioner experience)
- **Evidence Level**: Medium
- **Key Findings**:
  - Universal fetch function > hard-coded per-endpoint actions
  - Prompt quality is the #1 success factor
  - No contextual memory between interactions (stateless)
  - Significant iteration required; demos are misleading
  - Hybrid approach works: no-code agent + Forge function + no-code actions
  - Iterate prompts in no-code Studio first, then port to Forge
  - Noticeable latency with external API calls

### S4 — Hello World Rovo Agent Tutorial
- **URL**: https://developer.atlassian.com/platform/forge/build-a-hello-world-rovo-agent/
- **Type**: Official tutorial
- **Evidence Level**: Very High
- **Key Findings**:
  - Function receives payload with inputs + context object
  - Context includes cloudId, product-specific data (Jira issueKey/projectKey, Confluence contentId/spaceKey)
  - Prompt is the main behavior control: "The main way to change the behavior of your Agent is by modifying the prompt"
  - Action description tells agent *when* to invoke: "When a user asks to log a message, this action logs the message"
  - Must instruct agent in prompt to ask for missing required inputs

### S5 — Extending Atlassian Products with Rovo Agents
- **URL**: https://developer.atlassian.com/platform/forge/extend-atlassian-products-with-a-forge-rovo-agent/
- **Type**: Official documentation
- **Evidence Level**: Very High
- **Key Findings**:
  - Four pillars: custom data integration, strict logic delegation, enhanced data understanding, Forge capability leverage
  - "Delegate complex logic to your app" — agent handles NL, app handles computation
  - Cryptic field names hurt LLM comprehension — surface clear descriptions
  - Agents access only data in their installed workspace

### S6 — Opus Guard Case Study (Atlassian Engineering Blog)
- **URL**: https://www.atlassian.com/blog/developer/rethinking-ux-how-opus-guard-built-ai-assisted-data-governance-with-rovo-and-forge
- **Type**: Case study (vendor + Atlassian co-published)
- **Evidence Level**: High
- **Key Findings**:
  - CRUD action pattern: fetch-content (GET), fetch-classification-levels (GET), fetch-content-classification-level (GET), set-content-classification-level (UPDATE)
  - Prompt structure: Workflow layer > Jobs layer > Templates layer
  - Forge agents need explicit action-calling instructions (no built-in knowledge plugins)
  - Security: use `asUser()` for permission validation
  - Prompts that work in Studio often fail in Forge — different execution model
  - Iterate in Studio first, then adapt for Forge
  - Include response parsing instructions in prompt

### S7 — Jira Issue Analyst Tutorial
- **URL**: https://developer.atlassian.com/platform/forge/build-a-jira-issue-analyst-rovo-agent/
- **Type**: Official tutorial
- **Evidence Level**: Very High
- **Key Findings**:
  - Data minimization: return only key + summary, not full API response
  - Dynamic query construction based on available context
  - Optional inputs with graceful defaults
  - Multi-step workflow in prompt: check context > fetch > analyze > present
  - Tabular output format specified in prompt

### S8 — Rovo Agent Skills (Support Docs)
- **URL**: https://support.atlassian.com/rovo/docs/agent-actions/
- **Type**: Official documentation
- **Evidence Level**: Very High
- **Key Findings**:
  - Terminology shift: "actions" now called "skills"
  - Recommendation: fewer than 5 skills per agent
  - Bulk operations limited to 20 items max
  - Agents respect existing user permissions
  - Third-party skills in beta, require auth
  - In automation, agents provide text only (no skill execution)

### S9 — Rovo Example Apps
- **URL**: https://developer.atlassian.com/platform/forge/example-apps-rovo/
- **Type**: Official examples
- **Evidence Level**: High
- **Key Findings**:
  - Three reference apps: Jira Issue Analyst, Q&A Creator, Weather Forecaster
  - All use rovo:agent + action module pattern
  - @forge/api is the standard runtime
  - Pattern: one agent, multiple focused actions

### S10 — Rovo MCP Gallery (Atlassian Blog)
- **URL**: https://www.atlassian.com/blog/announcements/rovo-mcp-gallery
- **Type**: Official announcement
- **Evidence Level**: High
- **Key Findings**:
  - MCP (Model Context Protocol) is the new standard for external tool connection
  - Skills = "one specific task" granularity
  - Admins control which skills agents can access
  - Can connect to internal systems through MCP
  - Parallel path to Forge: MCP for simpler integrations, Forge for complex ones

### S11 — Rovo Chat and Teamwork Graph Updates
- **URL**: https://www.atlassian.com/blog/artificial-intelligence/rovo-chat-teamwork-graph-july-updates
- **Type**: Official blog
- **Evidence Level**: Medium (limited technical depth)
- **Key Findings**:
  - Teamwork Graph tracks: people, teams, projects, goals, work artifacts, app usage
  - Powers intent routing and contextual understanding
  - Personalized results grounded in actual work data
  - No public API for custom Teamwork Graph integration (proprietary)

---

## Evidence Level Criteria

| Level | Definition |
|-------|------------|
| Very High | Official developer documentation, canonical reference |
| High | Official blog/case study, or well-documented practitioner report |
| Medium | Community post, third-party analysis, or limited technical depth |
| Low | Speculative, outdated, or single-source claim |
