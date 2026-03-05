# rai External Agent — MVP Demo Spec

> What needs to be built for an external agent to use rai the same way a developer uses it with Claude Code.

---

## The gap

Today, using rai with Claude Code works like this:

```
Developer → /rai-session-start
  → CLI reads local files (session state, patterns, governance)
  → assembles context bundle
  → Claude loads it as system prompt
  → Claude has full rai context: where we are, what we know, what happened before

Developer works → /rai-session-close
  → CLI writes narrative, next_session_prompt, patterns to local files
  → next session picks up from there
```

An external agent (Forge app, Atlassian integration, any agent without filesystem access) **cannot do any of this** — it has no local files to read or write. It only has the server API.

The existing API lets an external agent query the graph and save patterns. But it cannot load session context or persist session continuity. Without that, every session starts from zero. That's not rai — that's a generic API.

---

## What MVP needs

Three endpoints. Nothing else is required for a working external demo.

---

### 1. `GET /api/v1/context/bundle`

**What it does:** Returns the same context bundle that `rai session start --context` produces via CLI. The agent loads this as its system prompt at the start of every session.

**Why it's MVP:** Without this, the agent doesn't know what story is active, what happened in previous sessions, or what the foundational patterns and governance rules are. It has no rai identity.

**What the response contains:**
```json
{
  "session_id": "SES-051",
  "bundle": "# Session Context\nDeveloper: Fer (shu)\nSession: SES-051\nStory: [...]\nEpic: ...\nBranch: ...\n\nLast: SES-050 — ...\n\n# Next Session Prompt\n...\n\n# Pending\n...\n\n# Available Context\n- governance: 14 items (~350 tokens)\n- behavioral: 11 items (~220 tokens)"
}
```

**Optional — priming sections on demand:**

```
GET /api/v1/context/sections?sections=governance,behavioral
```

Returns the full governance rules and foundational patterns. The agent requests these when it needs to go deeper than the summary in the bundle.

**What needs to exist in the DB for this to work:**
- Session state (current story, epic, branch, pending items, next_session_prompt, narrative)
- Developer profile (name, experience level, communication prefs)
- Graph with `always_on` and `foundational` pattern nodes

---

### 2. `POST /api/v1/context/close`

**What it does:** Persists session close data — narrative, next session prompt, and any patterns learned. Equivalent to `rai session close`.

**Why it's MVP:** Without this, every session leaves no trace. The next session starts from the same stale context. The "learning loop" that makes rai valuable over time doesn't work.

**Request body:**
```json
{
  "session_id": "SES-051",
  "summary": "Documented rai-server endpoints and identified MVP gaps",
  "narrative": "## Decisiones\n- Endpoint naming uses /context not /session...\n\n## Artifacts\n- packages/rai-server/README.md created",
  "next_session_prompt": "Continue with graph sync endpoint validation. Check if...",
  "patterns": [
    {
      "content": "Validate API payloads against source code before documenting",
      "context": ["documentation", "api"],
      "properties": {}
    }
  ]
}
```

**What it stores:**
- Updates session state in DB (narrative, next_session_prompt, summary)
- Inserts patterns via existing `memory_patterns` table

---

### 3. `POST /api/v1/ingest`

**What it does:** Accepts raw text content — a Confluence page, a document, a decision written in plain language — and the server extracts graph nodes from it. The agent doesn't need to know the node schema.

**Why it's MVP:** Without this, an external agent can only *read* the graph, not contribute to it. `POST /api/v1/graph/sync` requires the caller to already know how to build nodes and edges — that's CLI-level knowledge. An agent in Atlassian has documents, not pre-formatted nodes.

**Request body:**
```json
{
  "source": "confluence",
  "document_id": "PAGE-4521",
  "title": "Auth architecture decision",
  "content": "We decided to use SHA-256 for API key hashing. The main reasons were: irreversibility, no rainbow tables, standard in the industry. The raw key is never stored.",
  "url": "https://your-confluence/pages/4521",
  "properties": {}
}
```

**What it does internally:**
1. Creates a `GraphNodeRow` with `node_type` inferred from content or source
2. `content` maps directly to the node's `content` field
3. `document_id` + `source` become the `node_id`
4. Returns the created node ID

**What it does NOT do (to keep it simple):**
- No NLP or AI extraction in v1 — one document = one node
- No automatic edge inference — edges can be added via `/graph/sync` if needed
- Node type defaults to `"document"` unless caller specifies it

---

## What needs to exist in the DB

Currently the DB has no session state or developer profile tables. Those live in local YAML files on the developer's machine. To support the MVP endpoints, two new tables are needed:

**`developer_profiles`**
- `org_id`, `name`, `experience_level`, `communication_prefs`
- One per org for now (can expand to per-developer later)

**`session_state`**
- `org_id`, `session_id`, `current_story`, `current_epic`, `branch`
- `narrative`, `next_session_prompt`, `pending` (JSONB)
- `created_at`, `closed_at`

Everything else (patterns, graph nodes, events) already exists.

---

## Demo script with MVP built

```
1. GET /health                              → server up
2. GET /api/v1/context/bundle              → agent loads context, knows story S1.1 is active
3. GET /api/v1/context/sections?sections=governance  → agent loads governance rules
4. GET /api/v1/graph/query?q=auth          → agent queries what we know about auth
5. POST /api/v1/ingest                     → agent contributes a Confluence decision page
6. POST /api/v1/memory/patterns            → agent saves a pattern it learned
7. POST /api/v1/agent/events               → agent records "confluence.page.synced"
8. POST /api/v1/context/close              → agent closes session with narrative + next prompt
9. GET /api/v1/context/bundle              → next session: agent picks up exactly where it left off
```

This is rai. Same loop, different client.

---

## What is explicitly out of scope for MVP

- Team analytics or multi-developer dashboards
- Pattern reinforcement (voting)
- Real-time collaboration or conflict resolution
- Incremental graph sync (full rebuild is fine for demo)
- Per-developer profiles (one profile per org is enough)
- Authentication via OAuth (API key is sufficient)
