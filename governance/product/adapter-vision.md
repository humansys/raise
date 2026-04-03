# Adapter Vision — Deterministic I/O for Reliable AI Collaboration

> **Story:** RAISE-1000 (S650.9)
> **Date:** 2026-03-28
> **Authors:** Emilio + Rai
> **Status:** Draft — pending HITL review
> **Related:** `governance/product/pluggable-domains-vision.md`, ADR-033, ADR-034, ADR-041

---

## 1. Thesis

RaiSE treats documentation, specifications, backlog items, and plans as **first-order
artifacts** — parsed, indexed, and loaded into the agent's memory across sessions. They
must be as reliable as code. A misplaced scope doc, a wrongly-typed Jira issue, or a
Confluence page published to the wrong section compounds into corrupted context that
degrades every future session.

An LLM guided only by prompting and conversational context **cannot** reliably manage
these artifacts. It will:

- Create Jira issues with wrong transition IDs, missing required fields, or in the wrong project
- Publish Confluence pages to the wrong section of the page tree
- Lose track of which project a story belongs to between sessions
- Format backlog items differently each time, breaking downstream parsers

**Adapters exist to make the mechanical parts deterministic.** The LLM decides *what* to
do and *why*. The adapter handles *how* and *where* — with typed inputs, validated
outputs, and zero ambiguity.

This is not a convenience layer. It is a **reliability requirement**. Without adapters,
RaiSE cannot guarantee that its own governance artifacts are correct.

---

## 2. Current State

### What exists today

| Adapter | Protocol | Backend | Status |
| --- | --- | --- | --- |
| `AcliJiraAdapter` | `AsyncProjectManagementAdapter` | Jira via ACLI subprocess | Production |
| `McpConfluenceAdapter` | `AsyncDocumentationTarget` | Confluence via mcp-atlassian | Production |
| `FilesystemPMAdapter` | `ProjectManagementAdapter` | Local JSON files | Production |
| `BacklogHook` | `LifecycleHook` | Jira via adapter | Production |

### What works

- `rai backlog create/get/search/transition/comment/link` — full CLI surface for Jira
- `rai docs publish/get/search` — Confluence publishing and search
- `rai adapter check` — Protocol contract validation
- `rai mcp health` — connection health checks
- Declarative YAML adapters (ADR-041) — new backends without Python code
- Multi-instance Jira support in `.raise/jira.yaml`

### What doesn't work well

**Configuration is hand-written and fragile.** `.raise/jira.yaml` requires knowing
transition IDs, project keys, workflow states, and component names. A developer
setting up RaiSE for a new project must manually look these up in Jira admin. One
wrong ID and the adapter silently does the wrong thing.

**Confluence config is minimal.** `.raise/confluence.yaml` has exactly one field:
`space_key: rai`. No page tree routing, no artifact-type mapping, no template support.
Publishing goes to the right space but the *location within the space* depends on the
LLM or the skill knowing the page hierarchy.

**IssueSpec is incomplete.** Missing `component`, `fix_version`, and `parent_key` fields.
Skills that need these work around the adapter instead of through it.

**No validation against the live backend.** If your `jira.yaml` says transition ID 31 is
"In Progress" but your Jira instance maps it to "Code Review", nothing catches this
until a human notices the wrong status.

**No project routing.** A repo can participate in multiple Jira projects (e.g., `RAISE`
for framework, `RTEST` for test infrastructure). The adapter doesn't know which project
a given operation should target — the caller must specify every time.

---

## 3. Configuration Model

### Principle: Config that is generated, not written

A human should never need to know a Jira transition ID to configure RaiSE. The tooling
must discover it.

### Adapter Setup Skill (`/rai-adapter-setup`)

An interactive skill that:

1. **Discovers** the backend — queries Jira for available projects, workflows,
   transition IDs, components, versions, issue types
2. **Presents** options — "I found 3 projects: RAISE, RTEST, ACME. Which ones does
   this repo use?"
3. **Generates** correct YAML — `.raise/jira.yaml` with all IDs, mappings, and
   lifecycle events populated from the live backend
4. **Validates** immediately — runs the generated config against the backend to confirm
   correctness before saving

Same flow for Confluence:

1. Discover available spaces and their page trees
2. Present the space structure
3. Generate `.raise/confluence.yaml` with space key, section page IDs, artifact-type
   routing rules, and label conventions
4. Validate that the target pages exist

### Adapter Doctor (`rai adapter doctor`)

A diagnostic command that:

1. **Reads** current config (`.raise/jira.yaml`, `.raise/confluence.yaml`)
2. **Queries** the live backend
3. **Reports** mismatches:
   - "Transition ID 31 maps to 'Code Review' in your Jira, not 'In Progress'"
   - "Component 'rai-agent' does not exist in project RAISE"
   - "Confluence space 'rai' has no page at the expected Governance path"
4. **Suggests** fixes — either auto-fixable or with the correct values to paste
5. **Scores** overall health — pass/warning/error per section

Doctor runs as part of `rai doctor` (the general diagnostic) and can run standalone.

### Multi-Project Routing

A repo participating in multiple Jira projects needs routing rules:

```yaml
# .raise/jira.yaml
projects:
  RAISE:
    instance: humansys
    default: true          # operations without explicit project go here
    components: [rai-agent, raise-community, raise-pro]
    workflows:
      story: {backlog: 11, selected: 21, in_progress: 31, done: 41}
      bug: {backlog: 11, in_progress: 31, done: 41}

  RTEST:
    instance: humansys
    components: [test-infra]
    workflows:
      story: {backlog: 11, in_progress: 31, done: 41}
```

The adapter resolves the project from context: the story's Jira key prefix determines
which project config to use. Skills don't need to know — the adapter routes.

### Confluence Artifact-Type Routing

```yaml
# .raise/confluence.yaml
space_key: RaiSE1

routing:
  adr:
    parent: Architecture           # page title or ID
    template: tmpl-adr
    labels: [adr]
  epic-scope:
    parent: "Epics/{epic_key}: {epic_title}"
    template: tmpl-epic-scope
    labels: [epic, "epic:{epic_key}", "type:scope"]
  research:
    parent: Research
    template: tmpl-research-report
    labels: [research]
  skill:
    parent: "Skills/{category}"
    template: tmpl-skill-definition
    labels: [skill]
  session-archive:
    parent: "Sessions (Archive)"
    labels: [session, archive]
```

When `rai docs publish adr` runs, the adapter looks up the routing for `adr`, resolves
the parent page, applies the template, and sets labels. The LLM doesn't decide any of
this — the config does.

---

## 4. Adapter Protocols

### Existing Protocols

**ProjectManagementAdapter** — CRUD for work items:
- `create_issue`, `get_issue`, `update_issue`, `transition_issue`
- `batch_transition`, `link_to_parent`, `link_issues`
- `add_comment`, `get_comments`
- `search`, `health`

**DocumentationTarget** — Publish and search docs:
- `publish`, `get_page`, `search`, `can_publish`, `health`

### Missing Protocols

**SessionAdapter** — Session state persistence:
- `save_state`, `load_state`, `list_sessions`
- Today: direct file I/O to `session-state.yaml`
- Target: typed adapter that can persist to filesystem or remote

**ReleaseAdapter** — Release management:
- `check_readiness`, `bump_version`, `create_changelog`
- Today: `rai release check` and `rai release publish` do this inline
- Target: adapter that can also create GitHub/GitLab releases

**MetricsAdapter** — Telemetry and DORA metrics:
- `emit_event`, `query_metrics`
- Today: local JSONL telemetry
- Target: adapter that can feed dashboards

### Protocol Evolution

Protocols grow by adding optional methods with `NotImplementedError` defaults. Existing
adapters continue working. New methods are opt-in — if an adapter doesn't implement
`batch_create`, the CLI falls back to sequential `create_issue` calls.

---

## 5. Relationship to Domains

Adapters are **shared infrastructure** that Domains consume. They are not owned by any
Domain.

```text
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Work Domain  │  │  Governance  │  │   Project    │
│              │  │    Domain    │  │    Domain    │
│ requires:    │  │ requires:    │  │ requires:    │
│  PM Adapter  │  │  Docs Adapter│  │  Session Ad. │
│  Docs Adapter│  │              │  │  Release Ad. │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │    ┌────────────┤                 │
       │    │            │                 ��
  ┌────▼────▼──┐  ┌──────▼─────┐  ┌───────▼──────┐
  │ PM Adapter │  │Docs Adapter│  │Session/Release│
  │ (Jira)     │  │(Confluence)│  │ (Filesystem)  │
  └────────────┘  └────────────┘  └───────────────┘
```

A Domain declares which Adapter Protocols it requires. It does not care which concrete
implementation satisfies the protocol. This enables:

- **Backend swapping**: Linear instead of Jira, Notion instead of Confluence
- **Fallback chains**: Jira adapter → Filesystem adapter if Jira unavailable
- **Testing**: Mock adapters that satisfy the protocol without external dependencies

---

## 6. MVP for v2.4.0

The goal for 2.4.0 is **adapter reliability** — make the existing adapters correct and
complete enough that skills can trust them fully.

### Priority 1: Unblock existing skills

| Deliverable | Epic/Story | Why now |
| --- | --- | --- |
| Complete `IssueSpec` (component, fixVersion, parent_key) | RAISE-829 S829.1 | Skills create incomplete Jira issues |
| Fix `default_instance` blocker | RAISE-829 S829.7 / RAISE-744 | Adapter fails on fresh installs |
| Bug/Initiative lifecycle in BacklogHook | RAISE-829 S829.3 | Work Domain needs full lifecycle |
| Initiative issue type support | RAISE-829 S829.2 | Cannot create Initiatives via CLI |

### Priority 2: Confluence parity with Jira

| Deliverable | Epic/Story | Why now |
| --- | --- | --- |
| Artifact-type routing in publish | RAISE-830 S830.2 | Docs land in wrong location |
| Label support in DocumentationTarget | RAISE-830 S830.1 | Cross-cutting queries need labels |
| Index page auto-generation | RAISE-830 S830.3 | Manual maintenance is unsustainable |

### Priority 3: Config reliability

| Deliverable | Story | Why now |
| --- | --- | --- |
| Adapter setup skill (`/rai-adapter-setup`) | New | Config must be generated, not hand-written |
| Adapter doctor (`rai adapter doctor`) | New | Config must be validated against live backend |
| Confluence config expansion | New | `.raise/confluence.yaml` needs routing rules |

### Not in 2.4.0

- Session adapter (filesystem is fine for now)
- Release adapter (inline logic works)
- Metrics adapter (local JSONL is sufficient)
- Multi-backend fallback chains
- Adapter marketplace / third-party adapters

---

## 7. Backlog Map

How existing issues map to this vision:

### RAISE-829: Stabilize Backlog Adapter v2 (7 stories)

Core adapter reliability for Jira. Closes gaps identified in RAISE-760 gap analysis.

| Story | Maps to | Priority |
| --- | --- | --- |
| S829.1: Extend IssueSpec | §4 Protocol completeness | P1 |
| S829.2: Initiative type | §4 Protocol completeness | P1 |
| S829.3: Bug/Initiative lifecycle | §4 Protocol completeness | P1 |
| S829.4: Phase comments | §2 Observability (comments as audit trail) | P2 |
| S829.5: Selected for Dev event | §4 Protocol completeness | P2 |
| S829.6: Automation webhook URL | §3 Config model (automation section) | P2 |
| S829.7: Fix default_instance | §3 Config reliability | P1 (blocker) |

### RAISE-830: Stabilize Documentation Adapter v2 (6 stories)

Confluence parity — routing, labels, templates.

| Story | Maps to | Priority |
| --- | --- | --- |
| S830.1: Label support | §3 Confluence config | P1 |
| S830.2: Artifact-type routing | §3 Confluence routing model | P1 |
| S830.3: Index page generation | §3 Confluence IA support | P2 |
| S830.4: ConfluenceArchiveHook | §5 Domains consuming adapters | P2 |
| S830.5: Space template registration | §3 Config model | P3 |
| S830.6: Batch page tree creation | §3 Config model | P3 |

### New stories needed

| Story | Maps to | Scope |
| --- | --- | --- |
| Adapter setup skill (`/rai-adapter-setup`) | §3 Config generation | M — Jira discovery + YAML generation |
| Adapter doctor (`rai adapter doctor`) | §3 Config validation | S — read config, query backend, report |
| Confluence config expansion | §3 Confluence routing | S — expand YAML schema, routing rules |
| Unify RAISE-744 and S829.7 | §3 Config reliability | XS — deduplicate |

### Related but separate

| Issue | Relationship |
| --- | --- |
| RAISE-650 (Pluggable Domains) | Adapters are infrastructure that Domains consume |
| RAISE-831 (Compass Adapter) | New protocol, not current priority |
| RAISE-834 (Confluence Advanced) | Content properties + attachments, P3 |
| RAISE-743 (Stabilize Docs Adapter) | Superseded by RAISE-830 |
| RAISE-549 (Clean Jira references) | Tech debt, do alongside S829 work |
| RAISE-662 (Custom fields flag) | Nice-to-have, not blocking |
| RAISE-604 (signal emit-work multi-adapter) | Bug, fix alongside S829 work |

---

## Appendix: Design Decisions Captured

These decisions were made during the session of 2026-03-28 and should inform all adapter
work going forward:

1. **Adapters are shared infrastructure, not owned by Domains.** Multiple Domains
   consume the same adapter. The PM adapter serves both the Work Domain and any future
   Domain that needs to create Jira issues.

2. **Config is generated, not written.** If a human must know a Jira transition ID to
   configure RaiSE, we have failed. The setup skill discovers and generates.

3. **Validation is semantic, not just structural.** `rai adapter doctor` doesn't just
   check that YAML is valid — it checks that the values match the live backend.

4. **Confluence deserves the same config depth as Jira.** A single `space_key` field
   is not a configuration — it's a placeholder. Artifact-type routing, labels, and
   templates are required for deterministic doc publishing.

5. **Adapters evolve by optional methods.** New protocol methods default to
   `NotImplementedError`. Existing adapters don't break. This is progressive
   enrichment, not breaking changes.
