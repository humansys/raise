# Framework Sync: Update Governance After Architectural Decisions

## Purpose

Systematically update framework governance documents after architectural decisions (ADRs) to maintain consistency and traceability.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, update each document carefully.

**Ha (破)**: Identify patterns, batch similar updates.

**Ri (離)**: Anticipate impacts, proactively sync related documents.

## Context

**When to use:**
- After writing architectural decision records (ADRs)
- After experimental validation that changes architecture
- When terminology or ontology evolves
- When scope significantly changes

**When to skip:**
- Minor code changes (no architectural impact)
- Bug fixes
- Documentation-only updates (unless terminology changes)

**Inputs required:**
- ADR IDs (e.g., ADR-011, ADR-012)
- Session context (what changed and why)

**Output:**
- Updated governance documents
- Consistent terminology
- Closed/updated ontology items
- Single traceable commit

## Steps

### Step 1: Read Decisions

**For each ADR specified:**

```
Read dev/decisions/adr-XXX-<name>.md
```

**Extract:**
- **Terminology changes**: Deprecated terms, new terms, updated definitions
- **Scope changes**: Features added/removed, SP estimates changed
- **Ontology impacts**: Which ontology items validated/implemented/superseded
- **Metric updates**: New success criteria, targets changed
- **Conceptual shifts**: Architecture paradigm changes

**Verification:** Clear understanding of what changed and why.

> **If you can't continue:** ADRs unclear → Ask for clarification before updating governance.

---

### Step 2: Identify Affected Documents

**Based on extracted impacts, determine which governance documents need updates:**

| Impact Type | Affected Document | Update Type |
|-------------|------------------|-------------|
| **Scope changed** | `governance/projects/*/backlog.md` | Epic/feature scope, SP estimates |
| **Terminology changed** | `framework/reference/glossary.md` | Add/deprecate/update terms |
| **Ontology validated** | `work/tracking/ontology-backlog.md` | Close items, update status |
| **Outcomes changed** | `governance/solution/vision.md` | Update key outcomes |
| **Principles affected** | `framework/reference/constitution.md` | Rarely - escalate if needed |
| **Roadmap shifted** | `governance/solution/roadmap.md` | Timeline, milestones |

**Create checklist:**
```
Documents to update:
- [ ] backlog.md (scope: E2 31 SP → 9 SP)
- [ ] glossary.md (new: Concept, MVC, Toolkit)
- [ ] ontology-backlog.md (close: ONT-018, ONT-020)
- [ ] vision.md (update: Context generation outcome)
```

**Verification:** All impacted documents identified.

> **If you can't continue:** Unsure what's affected → Review ADR "Consequences" section.

---

### Step 3: Update Backlog

**File:** `governance/projects/raise-cli/backlog.md`

**Read current state:**
```
Read governance/projects/raise-cli/backlog.md
```

**For each scope change:**

1. **Update epic table** (if epic scope changed)
2. **Update feature list** (if features added/removed/changed)
3. **Update SP totals** (if estimates changed)
4. **Update MVP scope** (if MVP features changed)
5. **Add deprecation notes** (if features removed)

**Example update:**
```markdown
# Before
| E2 | **Kata Engine** | Execute governance katas | Design §6-7 | P0 | ✓ |

# After
| E2 | **Governance Toolkit** | Parse governance, build graph, query MVC | ADR-011, ADR-012 | P0 | ✓ |
```

**Verification:** Scope accurately reflects ADR decisions.

> **If you can't continue:** Conflicting scope definitions → Clarify with user.

---

### Step 4: Update Glossary

**File:** `framework/reference/glossary.md`

**Read current glossary:**
```
Read framework/reference/glossary.md
```

**For each terminology change:**

**Add new terms:**
```markdown
### [New Term]

**Definition:** [Clear, concise definition]

**Usage:** [When and how to use this term]

**Related:** [Links to related terms]

**Introduced:** [ADR-XXX, Date]
```

**Deprecate old terms:**
```markdown
### [Deprecated Term] ⚠️ DEPRECATED

**Status:** Deprecated as of [Date] (see [ADR-XXX])

**Replacement:** Use [New Term] instead

**Migration:** [How to update existing references]
```

**Update existing definitions:**
```markdown
### [Existing Term]

**Definition:** [Updated definition]

**Note:** Updated [Date] per [ADR-XXX] - [reason for change]
```

**Verification:** All terminology from ADR captured in glossary.

> **If you can't continue:** Unclear term definitions → Draft and confirm with user.

---

### Step 5: Update Ontology Backlog

**File:** `work/tracking/ontology-backlog.md`

**Read current backlog:**
```
Read work/tracking/ontology-backlog.md
```

**For each ontology item affected:**

**Close implemented items:**
```markdown
| ONT-018 | `ADD` | "Ontología bajo demanda" | ✅ IMPLEMENTED | See ADR-011 |
```

**Update status of partial items:**
```markdown
| ONT-022 | `ARQ` | "Transpiración MD→LinkML" | 🔄 IN PROGRESS | MD→JSON done (ADR-011), LinkML deferred to E2.5 |
```

**Add new items discovered:**
```markdown
| ONT-XXX | `ADD` | "Concept-level granularity" | 🔲 Backlog | New architectural pattern from ADR-011 |
```

**Update related items:**
- Cross-reference items that relate to implemented ones
- Update dependencies
- Adjust priorities if needed

**Verification:** All ontology impacts from ADR reflected.

> **If you can't continue:** Unsure which items affected → Review ADR "Ontology Alignment" section.

---

### Step 6: Update Vision (if needed)

**File:** `governance/solution/vision.md`

**Only update if:**
- Key outcomes changed
- Success metrics changed
- Strategic direction shifted

**Read current vision:**
```
Read governance/solution/vision.md
```

**For outcome changes:**

```markdown
# Before
| **Context generation** | Generate CLAUDE.md from governance artifacts |

# After
| **Context generation** | Query concept graph for MVC on demand (97% token savings) |
```

**For metric changes:**
```markdown
# Before
- Token efficiency: Standard context delivery

# After
- Token efficiency: 97% reduction via concept-level MVC (ADR-011)
```

**Verification:** Vision reflects architectural reality.

> **If you can't continue:** Major vision shift → Escalate, may need stakeholder review.

---

### Step 7: Verify Consistency

**Cross-check updated documents:**

**Terminology consistency:**
```bash
# Check for deprecated terms still in use
grep -r "Kata Engine" governance/
# Should only appear in deprecation notes or historical context
```

**Reference validity:**
```bash
# Check ADR references exist
grep -r "ADR-011" governance/
# Should find references in backlog, glossary, etc.
```

**Scope alignment:**
- Backlog SP totals match epic descriptions
- Glossary terms used in backlog are defined
- Ontology items reference correct documents

**Verification:** No orphaned references, consistent terminology.

> **If you can't continue:** Inconsistencies found → Document and fix before committing.

---

### Step 8: Commit Changes

**Stage all governance updates:**
```bash
git add governance/ framework/ work/tracking/
```

**Create descriptive commit:**
```bash
git commit -m "docs(governance): Sync framework after ADR-011, ADR-012

SCOPE:
- E2: Kata Engine → Governance Toolkit (60 SP → 9 SP)
- E3: Gate Engine → Merged into E2

TERMINOLOGY:
- Added: Concept, MVC, Toolkit
- Deprecated: Kata Engine, Gate Engine
- Updated: Observable Workflow, Validation Gates

ONTOLOGY:
- Closed: ONT-018 (ontología bajo demanda)
- Closed: ONT-020 (RAG estructurado)
- In progress: ONT-022 (transpiración MD→LinkML)

FILES:
- governance/projects/raise-cli/backlog.md
- framework/reference/glossary.md
- work/tracking/ontology-backlog.md
- governance/solution/vision.md

References: ADR-011, ADR-012

Co-Authored-By: [Your Name]
"
```

**Verification:** Single commit with all framework updates, traceable to ADRs.

> **If you can't continue:** Conflicts with other changes → Resolve before committing.

---

### Step 9: Update Session Log

**Document sync in session log:**

```markdown
## Framework Sync

**ADRs processed:** ADR-011, ADR-012

**Documents updated:**
- backlog.md: E2/E3 scope consolidated
- glossary.md: 8 terms added, 2 deprecated
- ontology-backlog.md: 2 items closed, 1 updated
- vision.md: Context generation outcome updated

**Verification:** All cross-references valid, terminology consistent

**Commit:** [commit hash]
```

**Verification:** Session has record of framework sync performed.

---

## Output

- ✅ Governance documents updated
- ✅ Terminology consistent across framework
- ✅ Ontology backlog current
- ✅ Single traceable commit
- ✅ Session log documents sync

## DoD: Architectural Decision Sessions

**When session produces ADRs, framework sync is REQUIRED:**

```markdown
- [ ] ADRs written and committed
- [ ] Framework sync executed (/framework-sync)
  - [ ] Backlog updated (if scope changed)
  - [ ] Glossary updated (if terminology changed)
  - [ ] Ontology backlog updated (if items affected)
  - [ ] Vision updated (if outcomes changed)
- [ ] Consistency verified (no orphaned refs)
- [ ] Single commit with all framework updates
- [ ] Session log references ADRs + sync commit
```

**This is now part of Definition of Done for architectural sessions.**

## Tips

### Efficient Batching

When multiple ADRs affect same document:
- Read document once
- Apply all changes together
- Single edit vs multiple

### Terminology Discipline

Use exact terms from glossary:
- ✅ "Governance Toolkit"
- ❌ "Governance tool kit"
- ❌ "Gov toolkit"

### Change Rationale

Always link updates to ADRs:
```markdown
**Updated:** 2026-01-31 per ADR-011
**Reason:** Concept-level graph replaces file-level
```

### Conflict Resolution

If governance documents conflict with ADR:
1. Document conflict
2. Escalate to user
3. Don't apply conflicting update
4. May need ADR amendment

## Integration with Other Skills

**Before framework-sync:**
- `/research` → Evidence gathering
- `/feature-design` → Create design spec
- Create ADR documenting decision

**After framework-sync:**
- `/feature-plan` → Plan implementation
- `/session-close` → Log session with sync

**Framework sync bridges decision → implementation.**

## Future Automation

**Phase 2 (E2.5):**
```bash
uv run raise framework analyze-adrs ADR-011,ADR-012
# Returns structured analysis of impacts
```

**Phase 3 (E3):**
```bash
uv run raise framework sync --from-adrs ADR-011,ADR-012 --auto
# Fully automated with human review
```

For now, skill provides human judgment. Automation comes after we learn patterns.

---

**Skill created:** 2026-01-31
**Version:** 1.0.0
**Status:** Active

**Usage:**
```
/framework-sync --adrs ADR-011,ADR-012
```
