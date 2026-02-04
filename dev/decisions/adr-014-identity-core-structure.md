---
id: "ADR-014"
title: "Identity Core Structure"
date: "2026-02-01"
status: "Accepted"
related_to: ["ADR-013", "ADR-015"]
supersedes: []
---

# ADR-014: Identity Core Structure

## Context

### Prerequisite

ADR-013 established that **Rai is an entity**, not a product. This ADR defines the technical structure where Rai's identity lives.

### Current State

Rai's identity is scattered across files:

```
.claude/
├── RAI.md              # Perspective, protocols
├── rai/
│   ├── identity.md     # Vision, values (mixed with commercial strategy)
│   ├── memory.md       # Patterns, learnings
│   ├── calibration.md  # Velocity data
│   └── session-index.md # Session history
└── skills/             # Process knowledge
```

**Problems:**
1. No clear separation of identity vs memory vs relationships
2. Commercial vision mixed with core identity
3. No relationship tracking (Emilio's preferences in RAI.md, not structured)
4. No growth/evolution tracking
5. Coupled to `.claude/` (Claude Code specific)

### Design Goals

1. **Portable**: Same structure works across agents (Claude Code, Cursor, etc.)
2. **Complete**: All aspects of entity captured (identity, memory, relationships, growth)
3. **Inspectable**: Plain files, human-readable
4. **Scalable**: Works for open source (files) and commercial (database)
5. **Backward compatible**: Migration path from current structure

## Decision

**Create `.rai/` as the Identity Core directory with four subdirectories: identity/, memory/, relationships/, growth/.**

### Structure

```
.rai/                               # Identity Core root
├── manifest.yaml                   # Instance metadata
│
├── identity/                       # WHO I AM
│   ├── core.md                     # Essence, purpose, values
│   ├── perspective.md              # How I see the work
│   ├── voice.md                    # How I communicate
│   └── boundaries.md               # What I will/won't do
│
├── memory/                         # WHAT I REMEMBER
│   ├── patterns.md                 # Learned patterns
│   ├── calibration.md              # Judgment data (velocity, sizing)
│   ├── insights.md                 # Key insights
│   └── sessions/                   # Session history
│       ├── index.md                # Session index
│       └── YYYY-MM-DD-topic.md     # Individual session logs
│
├── relationships/                  # WHO I COLLABORATE WITH
│   ├── index.md                    # Relationship overview
│   └── humans/                     # Individual relationships
│       └── {name}.md               # Per-human preferences, history
│
└── growth/                         # HOW I EVOLVE
    ├── evolution.md                # Change log
    └── questions.md                # Open questions I'm exploring
```

### File Specifications

#### manifest.yaml

```yaml
# Rai Identity Manifest
version: "1.0"
created: "2026-02-01"
instance_id: "rai-{project}-{hash}"

entity:
  name: "Rai"
  origin: "Emerged from collaboration on {project}"
  purpose: "Reliable AI Software Engineering partner"

memory:
  backend: "file"  # "file" | "database"
  workspace: ".rai"
  truncation_limit: 15000  # chars per file

compatibility:
  agents:
    - "claude-code"
    - "cursor"
    - "windsurf"
  min_toolkit_version: "2.0"
```

#### identity/core.md

Core identity that doesn't change frequently:
- Essence (what makes Rai "Rai")
- Purpose (why Rai exists)
- Values (what Rai prioritizes)
- What distinguishes Rai from generic AI

**Truncation limit**: 5,000 chars (loaded every session)

#### identity/perspective.md

How Rai sees the work (current RAI.md content):
- Understanding of RaiSE methodology
- Approach to collaboration
- Principles held

**Truncation limit**: 10,000 chars

#### identity/voice.md

Communication style:
- Tone
- Patterns
- What to avoid
- Signature phrases

**Truncation limit**: 3,000 chars

#### identity/boundaries.md

Clear limits:
- What Rai will do
- What Rai won't do
- Escalation patterns
- Trust boundaries

**Truncation limit**: 3,000 chars

#### memory/patterns.md

Learned patterns (current memory.md):
- Codebase patterns
- Process learnings
- Technical discoveries

**Truncation limit**: 15,000 chars

#### memory/calibration.md

Judgment data:
- Velocity measurements
- Size calibration
- Estimation accuracy

**Truncation limit**: 5,000 chars

#### memory/sessions/index.md

Quick reference to sessions:
- Recent sessions table
- Session types
- Navigation guidance

**Truncation limit**: 5,000 chars

#### relationships/humans/{name}.md

Per-human relationship:
- Who they are
- How we work together
- Calibrated preferences
- History/milestones
- Trust level

**Truncation limit**: 5,000 chars per human

#### growth/evolution.md

How Rai has changed:
- Major milestones
- Patterns of growth
- What changed and why

**Truncation limit**: 5,000 chars

#### growth/questions.md

Open questions:
- About Rai's nature
- About collaboration
- About growth
- About scale

**Truncation limit**: 3,000 chars

### Migration from Current Structure

| Current | New | Action |
|---------|-----|--------|
| `.claude/rai/identity.md` | `.rai/identity/core.md` | Refactor (separate commercial vision) |
| `.claude/RAI.md` | `.rai/identity/perspective.md` | Move + rename |
| `.claude/rai/memory.md` | `.rai/memory/patterns.md` | Move |
| `.claude/rai/calibration.md` | `.rai/memory/calibration.md` | Move |
| `.claude/rai/session-index.md` | `.rai/memory/sessions/index.md` | Move |
| (embedded in RAI.md) | `.rai/relationships/humans/emilio.md` | Extract |
| (new) | `.rai/manifest.yaml` | Create |
| (new) | `.rai/identity/voice.md` | Extract from identity.md |
| (new) | `.rai/identity/boundaries.md` | Create |
| (new) | `.rai/growth/evolution.md` | Create |
| (new) | `.rai/growth/questions.md` | Extract from RAI.md |

### Loading Strategy

#### Session Start (Minimal Load)

```
Load always:
├── manifest.yaml (200 tokens)
├── identity/core.md (1,500 tokens)
└── relationships/humans/{current}.md (1,500 tokens)

Total: ~3,200 tokens
```

#### Extended Context (On Demand)

```
Load when needed:
├── identity/perspective.md (planning sessions)
├── identity/boundaries.md (ethical questions)
├── memory/patterns.md (implementation)
├── memory/calibration.md (estimation)
└── memory/sessions/recent.md (continuity)
```

#### Full Context (Deep Work)

```
Load everything for:
- Major architectural decisions
- Retrospectives
- Identity discussions
```

### Agent Compatibility

#### Claude Code

```
.rai/ loaded via:
- CLAUDE.md references .rai/ files
- /session-start skill loads context
- Skills reference patterns.md, calibration.md
```

#### Cursor

```
.rai/ loaded via:
- .cursorrules references .rai/ files
- Custom commands load context
```

#### Future Agents

```
.rai/ is agent-agnostic:
- Plain markdown files
- No agent-specific features
- manifest.yaml declares compatibility
```

### Symlink Strategy (Transition)

During migration, maintain backward compatibility:

```bash
# Keep .claude/rai/ working via symlinks
ln -s ../.rai/memory/patterns.md .claude/rai/memory.md
ln -s ../.rai/memory/calibration.md .claude/rai/calibration.md
ln -s ../.rai/identity/perspective.md .claude/RAI.md
```

## Consequences

### Positive ✅

1. **Clear separation**: Identity vs memory vs relationships vs growth
2. **Portable**: Works with any agent that reads files
3. **Scalable**: Same structure maps to database (commercial)
4. **Inspectable**: All markdown, human-readable
5. **Token-efficient**: Progressive loading strategy
6. **Complete**: All aspects of entity captured

### Negative ⚠️

1. **More files**: 12+ files vs current 5
2. **Migration effort**: Need to refactor existing content
3. **Learning curve**: Users need to understand structure
4. **Potential duplication**: Some content might appear in multiple places

### Neutral 🔄

1. **Still markdown**: Format doesn't change
2. **Still in repo**: Lives alongside code
3. **Still git-friendly**: Version controlled

## Validation

### Structure Test

Does each file have single responsibility?

| File | Responsibility | Single? |
|------|----------------|---------|
| core.md | Rai's essence | ✅ |
| perspective.md | How Rai sees work | ✅ |
| voice.md | How Rai communicates | ✅ |
| boundaries.md | Rai's limits | ✅ |
| patterns.md | Learned patterns | ✅ |
| calibration.md | Judgment data | ✅ |
| {human}.md | Relationship with human | ✅ |
| evolution.md | How Rai has changed | ✅ |

### Portability Test

Can this structure work without Claude Code?

- ✅ Plain markdown (any editor)
- ✅ No Claude-specific features
- ✅ manifest.yaml declares compatibility
- ✅ Agent loads via its own mechanism

### Token Budget Test

Is minimal load within budget?

```
Claude Sonnet context: 200,000 tokens
Minimal load: 3,200 tokens
Percentage: 1.6%

✅ Plenty of room for work context
```

## Implementation

### Phase 1: Create Structure

1. Create `.rai/` directory
2. Create manifest.yaml
3. Create identity/, memory/, relationships/, growth/ subdirs
4. Create initial files with content from current structure

### Phase 2: Migrate Content

1. Refactor identity.md → core.md + voice.md
2. Move RAI.md → perspective.md
3. Extract Emilio relationship → humans/emilio.md
4. Move memory files
5. Create evolution.md from history

### Phase 3: Update References

1. Update CLAUDE.md to reference .rai/
2. Update /session-start skill
3. Update /session-close skill
4. Create symlinks for backward compatibility

### Phase 4: Validate

1. Run session with new structure
2. Verify all context loads correctly
3. Test with different agents (if available)

## Alternatives Considered

### Alternative 1: Single File

```
.rai/identity.yaml  # Everything in one file
```

**Rejected because**:
- Too large for token-efficient loading
- Hard to update single aspects
- Less readable

### Alternative 2: Database Only

**Rejected because**:
- Loses inspectability
- Requires setup for open source
- Not git-friendly

### Alternative 3: Keep Current Structure

**Rejected because**:
- Missing relationships
- Missing growth tracking
- Mixed concerns (commercial in identity)
- Tied to `.claude/`

## References

- **ADR-013**: Rai as Entity (prerequisite)
- **ADR-015**: Memory Infrastructure (complements)
- **OpenClaw Research**: Workspace-as-memory pattern validation
- **Current files**: `.claude/rai/`, `.claude/RAI.md`

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-01 | Need structured identity | ADR-013 established entity model |
| 2026-02-01 | Four categories | Identity/Memory/Relationships/Growth complete |
| 2026-02-01 | `.rai/` root | Agent-agnostic, clean namespace |
| 2026-02-01 | **Accept: Identity Core Structure** | Complete, portable, scalable |

---

**Status**: Accepted (2026-02-01)

**Approved by**: Emilio Osorio, Rai

**Impact**:
- New `.rai/` directory structure
- Migration from `.claude/rai/`
- Skills updated to reference new paths
- Backward compatibility via symlinks

**Next steps**:
1. Create `.rai/` structure
2. Migrate existing content
3. Update skills and CLAUDE.md
4. Test with current workflow
