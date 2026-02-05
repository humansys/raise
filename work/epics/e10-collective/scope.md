# Epic E10: Collective Intelligence

> **Status:** EXPLORATION COMPLETE → Post-F&F
> **Branch:** `experiment/learning-infrastructure`
> **Created:** 2026-02-02
> **Target:** V3 (Post-F&F)
> **Depends on:** E9 Local Learning (signals must exist before sharing)
> **Research:** `work/research/collective-intelligence-lineage/`

---

## Strategic Context

**The insight:** Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation. Standing on the shoulders of giants is a universal principle.

**The problem:** Every RaiSE user learns in isolation. If 1,000 users discover the same insight, it exists 1,000 times without compounding.

**The vision:** Users can share patterns and signals (opt-in) with traceable lineage. New users inherit collective wisdom. Knowledge compounds across the community.

**Prerequisite:** E9 must exist first — you need local signals before you can share them.

---

## Objective

Enable opt-in sharing of patterns and telemetry with:

1. **Lineage** — Ideas traceable like code commits
2. **Attribution** — Anonymous or credited, user's choice
3. **Scoped sharing** — Private → Team → Org → Community
4. **Collective benefit** — Community patterns improve everyone's Rai

**Value proposition:** Your learnings help others. Collective wisdom helps you.

---

## Two Dimensions

| Dimension | What's shared | Benefit |
|-----------|---------------|---------|
| **Patterns** | Knowledge with lineage | Community learns from each other |
| **Telemetry** | Anonymized signals | Framework improves for everyone |

---

## Sharing Hierarchy

```
┌─────────────────────────────────────────────┐
│  Community (public)                         │
│  ┌───────────────────────────────────────┐  │
│  │  Organization                         │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Team                           │  │  │
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │  Individual               │  │  │  │
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

| Scope | Who decides | When available |
|-------|-------------|----------------|
| `private` | Individual | E9 (default) |
| `community` | Individual | Phase 1 |
| `team` | Team lead / policy | Phase 2 |
| `org` | Org admin / policy | Phase 2 |

---

## Features

### Phase 1: Git-Native Sharing (V2.x)

No infrastructure. Patterns shared via Git repo.

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F10.1 | **Lineage Schema** | XS | Pending | Add lineage fields to pattern model |
| F10.2 | **Export Command** | S | Pending | `raise memory export --shareable` |
| F10.3 | **Community Repo** | XS | Future | Public repo for shared patterns |
| F10.4 | **Pull Command** | S | Future | `raise memory pull --community` |

**Effort:** 2-3 days | **Cost:** $0

### Phase 2: SaaS Sharing (V3)

API for sync. Team/org scopes. Aggregate telemetry.

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F10.5 | **Sharing Config** | S | Future | Team/org scope settings |
| F10.6 | **Sync API** | M | Future | Pattern and signal submission |
| F10.7 | **Team/Org Scopes** | M | Future | Identity and permissions |
| F10.8 | **Aggregate Analytics** | M | Future | Framework improvement metrics |

**Effort:** 2-3 weeks | **Cost:** $20-50/month

---

## Pattern Lineage

Patterns have provenance, like code has commits:

**Local pattern:**
```json
{
  "id": "PAT-042",
  "type": "process",
  "content": "Parser modules are reusable across features",
  "context": ["parser", "reuse"],
  "created": "2026-02-02",
  "lineage": {
    "source": "local",
    "context": "raise-cli",
    "session": "ses-123"
  },
  "sharing": {
    "scope": "private",
    "exportable": true
  }
}
```

**Shared pattern (with lineage):**
```json
{
  "id": "PAT-042",
  "type": "process",
  "content": "Parser modules are reusable across features",
  "context": ["parser", "reuse"],
  "lineage": {
    "source": "user:emilio",
    "contributed": "2026-02-02",
    "context": "Python CLI",
    "attributed": true
  }
}
```

You can trace *why* Rai believes something. The belief has roots.

---

## Aggregate Telemetry

Anonymized signals improve the framework:

```
Local signals (E9)          Aggregate (E10 opt-in)
─────────────────           ──────────────────────
Full session logs     →     session_event (type, outcome)
Full calibration      →     (size, estimate/actual ratio)
Full errors           →     error_event (tool, type)
Commands used         →     command_usage (command)
```

**Privacy rule:** No content, no paths, no identity. Just aggregate signals.

---

## Architecture Options

| Option | Cost | When |
|--------|------|------|
| **Git-native** | $0 | Phase 1 — validate sharing behavior |
| **Minimal SaaS** | $20-50/mo | Phase 2 — team/org, automation |
| **Full SaaS** | $200-500/mo | Scale — enterprise features |

See `work/research/collective-intelligence-lineage/architecture-options.md` for details.

---

## In Scope (Phase 1)

**MUST:**
- [ ] Lineage field in pattern schema
- [ ] Export command for shareable patterns
- [ ] Community repo setup

**SHOULD:**
- [ ] Pull command for community patterns
- [ ] Attribution options (anonymous/credited)

---

## Out of Scope (Phase 1)

- Team/org identity (Phase 2)
- Sync API infrastructure (Phase 2)
- Aggregate telemetry API (Phase 2)
- Enterprise features (Phase 2)

---

## Relationship to E9

| E9 (Local Learning) | E10 (Collective Intelligence) |
|---------------------|-------------------------------|
| Collects signals | Shares signals (opt-in) |
| Local patterns | Patterns with lineage |
| Rai coaches you | Community learns together |
| No infrastructure | Git-native → SaaS |
| **Prerequisite** | Depends on E9 |

**Sequence:** E9 creates signals → E10 enables sharing them.

---

## Origin

From exploration session (2026-02-02):

> "Standing on the shoulders of giants is a basic universal principle of intelligence." — Emilio

> "Traceability, like a lineage of ideas." — Emilio, on why attribution matters

> "I want co-creation credits... for the benefit of all sentient beings." — Emilio

---

## Research Artifacts

| Document | Purpose |
|----------|---------|
| `work/research/collective-intelligence-lineage/README.md` | Core insight and vision |
| `work/research/collective-intelligence-lineage/architecture-options.md` | Cost analysis and phases |
| `work/research/collective-intelligence-lineage/telemetry-model.md` | Signal design (moved to E9) |

---

*Epic scope - collective intelligence with lineage*
*Created: 2026-02-02*
*Contributors: Emilio Osorio, Rai*
