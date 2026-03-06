# rai-server API — External Agent Guide

How to use the existing rai-server API from an agent that lives outside the RaiSE CLI ecosystem (Atlassian Forge, custom agents, integrations).

## Base URL

```
http://your-rai-server:8000
```

## Authentication

Every request (except `/health`) requires an API key:

```
Authorization: Bearer rsk_<your_key>
```

The key is scoped to an organization. All data you read or write is isolated to your org.

---

## What you can do today

### 1. Check server availability

```
GET /health
```

No auth required. Use this before any session to verify the server is reachable.

```bash
curl http://localhost:8000/health
# {"status":"ok","database":"connected","version":"0.1.0"}
```

---

### 2. Query the knowledge graph

The graph contains nodes extracted from the project: patterns, decisions, governance rules, architecture concepts, skills. It's the project's knowledge base.

```
GET /api/v1/graph/query?q=<keyword>&limit=<n>
```

| Param | Required | Default | Description |
|---|---|---|---|
| `q` | yes | — | Keyword to search |
| `limit` | no | 20 | Max results (1–100) |

```bash
curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  "http://localhost:8000/api/v1/graph/query?q=authentication&limit=5"
```

Response:
```json
{
  "results": [
    {
      "node_id": "mod-auth",
      "node_type": "module",
      "scope": "project",
      "content": "API key authentication module",
      "source_file": "src/rai_server/auth.py",
      "properties": {},
      "rank": 0.06
    }
  ],
  "total": 1,
  "query": "authentication",
  "limit": 5
}
```

Each result gives you: what the concept is (`content`), where it lives (`source_file`), and how relevant it is (`rank`). Use `source_file` to know which file to read if you need to go deeper.

---

### 3. Push graph content (sync)

If you have structured knowledge to contribute — nodes and their relationships — you can push it to the graph. The sync is idempotent: running it twice with the same data is safe.

```
POST /api/v1/graph/sync
```

```json
{
  "project_id": "my-project",
  "nodes": [
    {
      "node_id": "decision-001",
      "node_type": "decision",
      "scope": "project",
      "content": "Use SHA-256 for API key hashing — irreversible, no rainbow tables",
      "source_file": null,
      "properties": {}
    }
  ],
  "edges": [
    {
      "source_node_id": "decision-001",
      "target_node_id": "mod-auth",
      "edge_type": "implements",
      "weight": 1.0,
      "properties": {}
    }
  ]
}
```

> **Note:** You need to know the schema to use this endpoint. If you have raw documents (Confluence pages, plain text), see the MVP roadmap — an `/ingest` endpoint is planned to handle unstructured content.

Response:
```json
{
  "status": "ok",
  "project_id": "my-project",
  "nodes_upserted": 1,
  "edges_created": 1,
  "edges_skipped": 0,
  "nodes_pruned": 0
}
```

---

### 4. Save a learned pattern

Patterns are reusable insights — things that should be remembered and applied in future work.

```
POST /api/v1/memory/patterns
```

```json
{
  "content": "Always validate the API payload against source code before documenting it",
  "context": ["documentation", "api"],
  "properties": {}
}
```

| Field | Required | Description |
|---|---|---|
| `content` | yes | The pattern text (1–10,000 chars) |
| `context` | no | Keywords for retrieval |
| `properties` | no | Arbitrary metadata |

Response: `{"id": "<uuid>", "status": "ok"}`

---

### 5. Retrieve saved patterns

```
GET /api/v1/memory/patterns?limit=<n>
```

Returns patterns saved by your org. Use these to prime your agent with accumulated knowledge before starting work.

```bash
curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  "http://localhost:8000/api/v1/memory/patterns?limit=50"
```

---

### 6. Record a telemetry event

Use this to log significant actions — story started, decision made, blocker found. Append-only, never modified.

```
POST /api/v1/agent/events
```

```json
{
  "event_type": "story.started",
  "payload": {
    "story_id": "s1.1",
    "agent": "forge-app"
  }
}
```

Payload is free-form JSON, max 100 KB.

---

### 7. List telemetry events

```
GET /api/v1/agent/events?limit=<n>
```

Returns recent events for your org. Useful for understanding what other agents have been doing.

---

## Typical session flow (today)

```
1. GET /health                          → verify server is up
2. GET /api/v1/memory/patterns          → load accumulated knowledge
3. GET /api/v1/graph/query?q=<topic>   → query relevant context
4. ... do your work ...
5. POST /api/v1/memory/patterns         → save what you learned
6. POST /api/v1/agent/events            → record what happened
```

---

## Node types reference

When building graph nodes, use these types for consistency with the RaiSE ecosystem:

| Type | Use for |
|---|---|
| `pattern` | Learned practices and heuristics |
| `decision` | Architecture or design decisions |
| `principle` | Guiding values and rules |
| `guardrail` | Code standards and constraints |
| `epic` | Epic-level work items |
| `story` | Story-level work items |
| `session` | Session records |
| `skill` | Agent skill metadata |
| `module` | Code modules from discovery |
| `component` | System components |
