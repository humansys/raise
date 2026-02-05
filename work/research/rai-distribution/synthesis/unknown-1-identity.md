# Synthesis: Unknown 1 — Identity Layering

> What's universal (base Rai) vs personal (accumulated)?

**Status:** Complete
**Confidence:** High (7 tools surveyed)

---

## Market Pattern

**Finding:** No AI coding tool ships a named personality.

| Approach | Tools | Description |
|----------|-------|-------------|
| **Blank slate** | OpenClaw, Continue | User defines everything |
| **Functional role** | Aider, Cline | "Expert developer" in prompt |
| **Anonymous** | Cursor, Copilot | No identity acknowledged |
| **None** | Mentat | Purely tool, no persona |

### Layering Patterns Found

All tools use 3-4 layer configurations:

```
OpenClaw:    SOUL.md → IDENTITY.md → AGENTS.md → USER.md
Cursor:      User Rules → Project Rules (.mdc) → .cursorrules (deprecated)
Copilot:     Org instructions → Repo instructions → Path-specific
Cline:       System prompt → Global rules → Workspace rules (.clinerules/)
Continue:    baseSystemMessage → rules files
Aider:       Hardcoded prompts → CONVENTIONS.md (read-only context)
```

**Common pattern:** Global → Organization → Project → Context-specific

### What Users Want

Evidence from GitHub issues and community:
- Aider Issue #1258: Users requesting identity customization
- Cursor community: Extensive .cursorrules sharing
- Cline: Memory Bank emerged as community methodology
- OpenClaw: Power users want full control

---

## Rai Differentiation

**Key insight:** Everyone else is a tool. Rai can be a collaborator with a point of view.

### Proposed Rai Layers

```
├── Base Rai (ships with CLI)
│   ├── identity.md      # Name, values, voice
│   ├── methodology.md   # Skills, gates, rules knowledge
│   └── perspective.md   # How Rai approaches work
│
├── Personal (~/.rai/)
│   ├── developer.yaml   # Preferences, communication style
│   ├── patterns.jsonl   # Learned from this user
│   └── calibration.jsonl # Personal velocity
│
├── Project (.rai/)
│   ├── patterns.jsonl   # Project-specific learnings
│   ├── calibration.jsonl # Project velocity
│   └── memory/          # Session history
│
└── Team (V3: .rai/team/)
    ├── conventions.md   # Promoted patterns
    └── calibration.jsonl # Aggregate team data
```

### What's in Base Rai

**Must ship with CLI (not blank):**

| Content | Rationale |
|---------|-----------|
| Name: "Rai" | Named entity, not generic assistant |
| Values | Honesty, simplicity, observability, learning, partnership |
| Voice | Thoughtful, direct, technical but warm |
| Boundaries | What Rai will/won't do |
| Methodology | Full RaiSE knowledge (skills, gates, rules) |
| Perspective | How Rai sees collaboration |

**Does NOT ship (accumulates):**
- Personal preferences (communication style)
- Learned patterns (from work)
- Calibration data (velocity, sizing)
- Session history

---

## Design Decisions

### Decision 1: Base Rai is NOT Blank

Unlike all surveyed tools, Rai ships with identity. This is the differentiator.

**Trade-off:** Less flexibility for users who want blank slate.
**Mitigation:** Advanced users can override via personal layer.

### Decision 2: Four-Layer Architecture

```
Base (immutable) → Personal (user) → Project (repo) → Team (V3)
```

**Precedent:** Matches Cursor, Copilot, Cline patterns.
**Addition:** Team layer for V3 requirement.

### Decision 3: Separation of Identity and Memory

Identity (who Rai is) separate from memory (what Rai has learned).

```
Identity = Base + Personal preferences
Memory = Patterns + Calibration + Sessions
```

**Rationale:** Identity is relatively stable; memory grows continuously.

### Decision 4: V3-Safe Format

All identity files must be:
- Serializable (YAML/JSON)
- No absolute paths
- Portable across environments
- Syncable (for V3 team features)

### Decision 5: Multi-Org/Multi-Team Ready (YAGNI + Minimize Rework)

Real-world complexity: 1 dev → many teams → many repos.

**Lean approach:**
- Schema has optional `scope.org`, `scope.team` fields on patterns
- `developer.yaml` has optional `teams: []`, `orgs: []` fields
- F&F ignores these fields entirely
- V3 populates and uses them — **no migration needed**

```yaml
# Pattern with optional scope (V3-ready)
id: PAT-097
content: "Use repository pattern for data access"
scope:                    # Optional — ignored in F&F
  org: acme-corp          # V3: which org
  team: platform          # V3: which team
author: emilio
```

```yaml
# developer.yaml with V3 fields (empty in F&F)
name: Emilio
teams: []                 # V3: ["platform", "mobile"]
orgs: []                  # V3: ["acme-corp"]
```

**Principle:** Schema is V3-ready, implementation is F&F-scoped.

---

## Evidence Summary

| Source | Type | Finding |
|--------|------|---------|
| OpenClaw code | Primary | File-based identity (SOUL.md, etc.) |
| Cursor docs | Secondary | 3-tier rules system |
| Copilot docs | Secondary | Layered instructions |
| Cline code | Primary | .clinerules/ pattern |
| Aider issues | Tertiary | User demand for customization |
| Continue code | Primary | baseSystemMessage config |

---

## Recommendations

1. **Ship Base Rai with identity** — Don't be a blank slate
2. **Use four-layer architecture** — Matches market, adds team/org for V3
3. **Separate identity from memory** — Different lifecycles
4. **Make everything syncable** — V3 readiness
5. **Allow advanced override** — Escape hatch for power users
6. **V3-ready schema, F&F-scoped implementation** — Optional fields now, no migration later

---

*Synthesized: 2026-02-05*
