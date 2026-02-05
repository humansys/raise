# Synthesis: Unknown 4 — Team Learning (V3)

> How do multiple developers contribute to shared Rai knowledge?

**Status:** Complete
**Confidence:** Medium (emerging patterns, less market validation)
**Priority:** V3 (post-F&F), but architecture decisions affect F&F

---

## V3 Constraint

**HARD REQUIREMENT:** Before public V3 release, RaiSE will be used in a team setting where Rai learns from all developers and improves.

This means E14 identity format must be syncable from day 1.

---

## Multi-Org/Multi-Team Reality

**Real-world complexity (not the simple model):**

```
Organization (Acme Corp)
├── Team: Platform
│   ├── Repo: api-gateway
│   ├── Repo: auth-service
│   └── Repo: shared-libs
├── Team: Mobile
│   ├── Repo: ios-app
│   ├── Repo: android-app
│   └── Repo: shared-libs  ← shared with Platform
└── Team: Data
    └── Repo: analytics-pipeline

Developer: Emilio
├── Member of: Platform, Mobile
├── Works on: api-gateway, shared-libs, ios-app
└── Personal patterns apply to ALL
```

**Problems this creates:**
1. Where do Platform team patterns live? In which repo?
2. `shared-libs` has two teams — whose patterns win?
3. Developer's personal patterns need to work across all repos
4. Org-wide conventions have no single home

### Lean Approach (KISS + YAGNI + Minimize Rework)

| Principle | Application |
|-----------|-------------|
| **KISS** | F&F ignores team/org fields entirely |
| **YAGNI** | Don't build team loaders until V3 |
| **DRY** | One pattern format, multiple loaders |
| **Minimize rework** | Schema has optional fields now → no migration later |

**One-liner:** Schema is V3-ready, implementation is F&F-scoped.

---

## Market Pattern

**Finding:** Current tools share rules/conventions, NOT learning.

| Tool | What's Shared | Learning Shared? |
|------|---------------|------------------|
| Cursor Teams | Project memory, team rules | Rules yes, patterns no |
| Copilot Enterprise | Copilot Spaces, org instructions | Context yes, learning no |
| Continue.dev | Shareable Agents | Definitions yes, learning no |
| Aider | CONVENTIONS.md | Manual file sharing |
| Windsurf | Rules files | Rules yes, patterns no |
| Tabnine | Org fine-tuned model | Model-level (unique) |
| OpenClaw | Isolation-first | Explicit sharing only |

**Gap:** True team learning (patterns from one dev benefiting others) is unsolved.

### Closest Solution: Tabnine

Tabnine fine-tunes an org-level model on team's code. But:
- Requires enterprise tier
- Model-level, not pattern-level
- No transparency on what's learned

---

## Memory Architecture Patterns

### Letta (MemGPT)

```
Core Memory (in-context)     Archival Memory (vector DB)
├── persona block            ├── searchable
├── human block              ├── unlimited size
└── working memory           └── agent self-edits
```

**Key insight:** Agent self-edits memory. Structured XML blocks.

### LangMem

```
Namespace: (org, team, user, memory_type)

Memory Types:
├── Semantic (facts, concepts)
├── Episodic (events, experiences)
└── Procedural (how-to, patterns)
```

**Key insight:** Namespace isolation enables sharing control.

### ICML 2025: Collaborative Memory

```
Private Tier          Shared Tier
├── user-only         ├── team-visible
├── no sync           ├── promoted content
└── full history      └── provenance tracked
```

**Key insight:** Promotion model — content explicitly moved from private to shared.

---

## Privacy Boundary

### What Should Stay Personal

| Content | Why Personal |
|---------|--------------|
| Communication style | Individual preference |
| Raw velocity numbers | Psychological safety |
| Mistakes/failures | Learning without judgment |
| Work-in-progress patterns | Not yet validated |

### What Can Be Team-Shared

| Content | Why Shareable |
|---------|---------------|
| Successful patterns | Benefit everyone |
| Project conventions | Team consistency |
| Aggregate calibration | Planning accuracy |
| Validated learnings | Proven value |

---

## Conflict Resolution

**Problem:** Two developers learn contradictory patterns.

### Approaches

| Approach | Mechanism | Trade-off |
|----------|-----------|-----------|
| **Last write wins** | Simple timestamp | Loses nuance |
| **Voting** | Team consensus | Slow, overhead |
| **Provenance-based** | Track success_count | Requires metrics |
| **Scoped validity** | Pattern applies to context X | Complexity |

### Recommendation: Provenance + Review

```yaml
# Promoted pattern with provenance
- id: PAT-TEAM-001
  content: "Use repository pattern for data access"
  promoted_by: emilio
  promoted_date: 2026-02-10
  source_pattern: PAT-097  # Original personal pattern
  success_count: 5
  context: "Python projects with SQLAlchemy"
  status: active  # or deprecated, contested
```

**Conflict resolution:** When patterns conflict, flag as "contested" and surface to team lead for decision.

---

## Recommended Architecture

### V3-Ready Schema (Implemented in F&F)

```yaml
# Pattern schema — same format F&F and V3
id: string
content: string
created: datetime
author: string
scope:                    # Optional — absent means "personal"
  org: string?            # V3: organization name
  team: string?           # V3: team name
  project: string?        # Project path (for cross-repo V3)
success_count: int?
context: string?          # When this applies
```

```yaml
# ~/.rai/developer.yaml — V3-ready fields
name: Emilio
teams: []                 # F&F: empty. V3: ["platform", "mobile"]
orgs: []                  # F&F: empty. V3: ["acme-corp"]
# ... rest unchanged
```

**F&F behavior:**
- `scope` absent or ignored → pattern is personal/project
- `teams: []`, `orgs: []` → no team features
- `.rai/team/` → optional, git-shared if used manually

**V3 additions (no migration needed):**
- Populate `scope` on promotion
- Populate `teams`/`orgs` from SSO
- Add external pattern loaders (team repos, cloud)
- Add conflict resolution logic

### Four-Layer Model (V3-Ready)

```
├── Base Rai (immutable per version)
│   └── Ships with CLI
│
├── Personal (~/.rai/)
│   ├── Syncs to user's cloud account (V3)
│   ├── Private patterns, calibration
│   └── Never shared without explicit action
│
├── Project (.rai/)
│   ├── Committed to git
│   ├── Shared via normal git flow
│   └── Project-specific patterns
│
└── Team/Org [V3]
    ├── Team patterns: loaded from team repos or cloud
    ├── Org patterns: loaded from org-level config
    └── Inheritance: org → team → project → personal (most specific wins)
```

### Inheritance Model (V3)

Inheritance is a **query** concern, not a **storage** concern.

```python
# F&F query (simple)
patterns = load_project_patterns() + load_personal_patterns()

# V3 query (adds team/org filtering)
patterns = (
    load_org_patterns(user.orgs) +
    load_team_patterns(user.teams) +
    load_project_patterns() +
    load_personal_patterns()
)
# Most specific wins on conflict (personal > project > team > org)
```

### Promotion Flow (V3)

```
Personal Pattern (mine)
        │
        │ /promote-pattern PAT-097
        ▼
Team Review (optional)
        │
        │ approved
        ▼
Team Pattern (.rai/team/patterns.jsonl)
        │
        │ git commit + push
        ▼
Available to All Team Members
```

### F&F Simplification

For F&F release:
- Personal: `~/.rai/developer.yaml` (local only)
- Project: `.rai/` (git-shared as today)
- Team: Not implemented (manual pattern sharing via git)

**V3 additions:**
- Personal sync to cloud
- Team layer with promotion
- Aggregate calibration

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Alternative |
|--------------|---------|-------------|
| Auto-aggregation | Privacy risk, noise | Explicit promotion |
| Real-time sync | Complexity, offline breaks | Git-native, async |
| Velocity comparison | Psychological safety | Aggregate only |
| Inherited permissions | Context bleed | Explicit boundaries |
| No provenance | Can't trust or debug | Track everything |

---

## Evidence Summary

| Source | Type | Finding |
|--------|------|---------|
| Cursor docs | Secondary | Team rules, not learning |
| Copilot docs | Secondary | Spaces for context, not patterns |
| Letta/MemGPT | Primary | Self-editing memory architecture |
| LangMem docs | Secondary | Namespace-based isolation |
| ICML 2025 paper | Secondary | Private/shared tiers |
| Tabnine | Tertiary | Org model fine-tuning |

---

## Recommendations

### For E14 (F&F)

1. **V3-safe format** — All identity/memory files syncable
2. **No absolute paths** — Portable across environments
3. **Provenance from start** — Track author, date, source on patterns
4. **Git-native** — Team sharing via normal git flow

### For V3 (Post-F&F)

1. **Personal sync** — Cloud backup for `~/.rai/`
2. **Team layer** — `.rai/team/` with promotion model
3. **Aggregate calibration** — Team velocity without individual exposure
4. **Conflict handling** — Provenance + contested status + team lead review

---

## Implementation Sketch (V3)

```python
# Pattern promotion command
@app.command()
def promote_pattern(
    pattern_id: str,
    context: str = None,
    skip_review: bool = False
):
    """Promote a personal pattern to team level."""

    # Load personal pattern
    personal = load_personal_patterns()
    pattern = personal.get(pattern_id)

    if not pattern:
        raise ValueError(f"Pattern {pattern_id} not found")

    # Create team pattern with provenance
    team_pattern = TeamPattern(
        id=generate_team_pattern_id(),
        content=pattern.content,
        promoted_by=get_current_user(),
        promoted_date=datetime.now(),
        source_pattern=pattern_id,
        success_count=pattern.success_count,
        context=context,
        status="pending_review" if not skip_review else "active"
    )

    # Write to team patterns
    team_path = Path(".rai/team/patterns.jsonl")
    append_jsonl(team_path, team_pattern)

    console.print(f"Pattern promoted to team: {team_pattern.id}")
    console.print("Remember to commit and push .rai/team/")
```

---

*Synthesized: 2026-02-05*
