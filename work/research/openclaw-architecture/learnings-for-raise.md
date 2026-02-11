# Learnings from OpenClaw for RaiSE

> Actionable recommendations extracted from OpenClaw architecture research.
> **Date:** 2026-02-01

---

## Summary Matrix

| Pattern | OpenClaw Implementation | RaiSE Current | Recommendation | Priority |
|---------|------------------------|---------------|----------------|----------|
| Workspace-as-memory | AGENTS.md, SOUL.md, MEMORY.md | `.claude/rai/memory.md` etc. | Formalize conventions | HIGH |
| Pre-compaction flush | Soft threshold + silent write | None | Implement for V3 | HIGH |
| Minimal agent core | 4 tools (Read, Write, Edit, Bash) | Skills + Toolkit | Validated | - |
| Typed pipelines | Lobster with approval gates | Katas as markdown | Consider hybrid | MEDIUM |
| Gateway abstraction | WebSocket control plane | CLI only | V3 multi-interface | MEDIUM |
| Skills ecosystem | 700+ JS/TS functions | Skills as markdown guides | Consider hybrid | LOW |

---

## HIGH Priority: Workspace-as-Memory

### OpenClaw Pattern

```
~/.openclaw/workspace/
├── AGENTS.md        # Instructions + memory
├── SOUL.md          # Persona, tone, boundaries
├── USER.md          # User profile
├── IDENTITY.md      # Agent identity
├── MEMORY.md        # Long-term (private sessions only)
├── memory/
│   ├── 2026-02-01.md  # Today
│   └── 2026-01-31.md  # Yesterday (also loaded)
└── skills/
```

**Key rules:**
- Files are the source of truth
- Today + yesterday loaded at session start
- 20,000 char truncation per file
- MEMORY.md only in private sessions

### Current RaiSE Structure

```
.claude/
├── RAI.md           # Perspective + protocols
├── rai/
│   ├── identity.md     # V3 vision
│   ├── memory.md       # Patterns, learnings
│   ├── calibration.md  # Velocity data
│   └── session-index.md # Session history
└── skills/          # Process guides
```

### Recommendation

**Option A: Align with OpenClaw naming**
- Rename `RAI.md` → `SOUL.md`
- Rename `memory.md` → `MEMORY.md`
- Add `USER.md` for Emilio preferences
- Adopt truncation limits (20K chars)

**Option B: Keep our names, adopt their patterns**
- Keep `.claude/rai/` structure
- Add truncation limit guidance
- Add "yesterday" loading pattern
- Document file purposes explicitly

**My preference:** Option B — our names are meaningful and documented. Adopt their **patterns**, not their **names**.

### Immediate Actions (V2)

1. Add `## Truncation Limit` section to memory.md: "Keep under 15,000 characters"
2. Update `/session-start` to load yesterday's session log if available
3. Document file purposes in a README inside `.claude/rai/`

---

## HIGH Priority: Pre-Compaction Memory Flush

### OpenClaw Pattern

```
Session tokens approach soft threshold
    ↓
Silent agentic turn (NO_REPLY flag)
    ↓
Agent writes critical state to memory/YYYY-MM-DD.md
    ↓
Compaction proceeds safely
```

**Configuration:**
```json
{
  "compaction": {
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  },
  "preCompactionFlush": {
    "enabled": true,
    "softThresholdTokens": 4000
  }
}
```

### Current RaiSE Approach

- `/session-close` skill for manual memory updates
- No automatic detection of context limits
- Risk of losing state in long sessions

### Recommendation

**For V3:** Implement automatic memory flush before context compaction.

**Implementation sketch:**
1. Monitor session token usage (Claude Code may expose this)
2. At soft threshold (e.g., 80% of context window):
   - Trigger silent memory write
   - Update `memory/YYYY-MM-DD.md` with:
     - Decisions made
     - Progress state
     - Open questions
3. Continue normally after flush

**Alternative for V2:** Document manual checkpoints:
- "At natural breaks (story complete, design approved), run `/session-close`"
- Add checkpoint reminders to skill steps

### Immediate Actions

1. Add to `/session-close`: "Run proactively at natural checkpoints, not just session end"
2. Research Claude Code token monitoring capabilities
3. Add to V3 backlog: "Implement pre-compaction flush"

---

## MEDIUM Priority: Typed Workflow Pipelines (Lobster-inspired)

### OpenClaw Pattern

```yaml
name: deploy-preview
args:
  branch: { default: "main" }
steps:
  - id: build
    run: npm run build
  - id: test
    run: npm test
    condition: $build.exitCode == 0
  - id: approve_deploy
    approval: true
    prompt: "Deploy to preview?"
  - id: deploy
    run: vercel deploy
    condition: $approve_deploy.approved
```

**Benefits:**
- Single invocation for multi-step operations
- Approval gates built in
- Resume tokens for interrupted flows
- Auditable (pipelines are data)

### Current RaiSE Approach

- Katas are markdown process guides
- AI reads and executes steps
- No formal approval gates beyond HITL checkpoints
- No resume capability

### Recommendation

**Hybrid approach:** Keep markdown katas, add execution metadata.

**Potential kata enhancement:**
```markdown
## Step 3: Validate Design

**Gate:** approval_required
**Resume:** step3_design_validated

[Step content...]

**Verification:** Design covers all acceptance criteria.
```

**For V3:** Consider `rai workflow run kata.md` that:
1. Parses kata markdown
2. Extracts steps and gates
3. Executes with approval checkpoints
4. Supports resume from any step

### Immediate Actions

1. Add to parking lot: "Explore Lobster-inspired kata execution for V3"
2. Review current katas for implicit approval gates
3. Consider adding `**Gate:**` markers to existing katas

---

## MEDIUM Priority: Gateway Pattern for Multi-Interface

### OpenClaw Pattern

```
Gateway (single control plane)
    │
    ├── WhatsApp
    ├── Telegram
    ├── Slack
    ├── Discord
    └── WebChat
```

Agent intelligence stays constant; gateway adapts to interface.

### Current RaiSE Approach

- CLI only (`rai` command)
- Claude Code integration via skills
- No multi-interface support

### Recommendation

**For V3:** Design gateway abstraction for:
- Jira (create issues, update status)
- Confluence (read/write docs)
- Rovo Dev (Atlassian agentic platform)
- CLI (current)
- MCP server (future)

**Architecture sketch:**
```
┌─────────────────────────────────────┐
│           Rai Gateway               │
│   (Protocol adaptation layer)       │
└─────────────────────────────────────┘
        │           │           │
        ▼           ▼           ▼
    ┌───────┐  ┌───────┐  ┌───────┐
    │ Jira  │  │ Rovo  │  │  CLI  │
    │Adapter│  │Adapter│  │Adapter│
    └───────┘  └───────┘  └───────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
            ┌─────────────┐
            │ Rai Core    │
            │ (Skills +   │
            │  Toolkit +  │
            │  Judgment)  │
            └─────────────┘
```

### Immediate Actions

1. Add to V3 backlog: "Design gateway abstraction for multi-interface"
2. Research Rovo Dev API requirements
3. Keep current architecture clean for future gateway integration

---

## LOW Priority: Skills Ecosystem

### OpenClaw Pattern

- 700+ community skills
- JSON schema + JS/TS implementation
- ClawHub marketplace
- Self-referential (skills describing skills)

### Current RaiSE Approach

- Skills as markdown process guides
- AI reads and interprets
- No code execution in skills themselves
- CLI toolkit provides deterministic operations

### Recommendation

**Keep current approach for V2.** Our skills are for process orchestration, not code execution. The CLI toolkit handles deterministic operations.

**For V3+:** Consider hybrid:
- Markdown: Process guide for AI
- JSON schema: Tool description for LLM
- Python/TS: Validation + deterministic operations

**Example hybrid skill:**
```
skills/
└── story-design/
    ├── README.md       # Process guide (AI reads)
    ├── schema.json     # Tool description (LLM)
    └── validate.py     # Validation code (CLI toolkit)
```

### Immediate Actions

1. Keep current skills architecture
2. Add to V3+ backlog: "Explore hybrid skills (markdown + schema + validation)"
3. Watch OpenClaw skills ecosystem for patterns

---

## V2 Immediate Actions Summary

| Action | Where | Effort |
|--------|-------|--------|
| Add truncation guidance to memory.md | `.claude/rai/memory.md` | XS |
| Add "yesterday" loading to /session-start | Skill update | S |
| Document checkpoint discipline | `/session-close` skill | XS |
| Add pre-compaction flush to V3 backlog | `dev/parking-lot.md` | XS |
| Add gateway abstraction to V3 backlog | `dev/parking-lot.md` | XS |

---

## V3 Backlog Items (from this research)

1. **Pre-compaction memory flush** — Automatic state preservation
2. **Gateway abstraction** — Multi-interface support (Jira, Rovo, CLI)
3. **Typed kata execution** — Lobster-inspired with approval gates
4. **Hybrid skills** — Markdown + schema + validation code
5. **Token monitoring** — Session context usage tracking

---

## Key Insight

OpenClaw validates the direction. Their success proves:
- Workspace-as-memory works
- Minimal core + extensibility beats bloat
- Typed pipelines add reliability
- Community ecosystem can explode quickly

What they lack, we provide:
- **Governance** (Jidoka, quality gates)
- **Methodology** (katas, skills, process)
- **Judgment** (calibrated estimates, push-back)
- **Accumulated intelligence** (cross-project patterns)

**Our positioning:** "OpenClaw gives you capability. Rai gives you capability with calibrated professional judgment."

---

*Research complete. Ready for implementation decisions.*
