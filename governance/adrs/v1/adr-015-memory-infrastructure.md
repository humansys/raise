---
id: "ADR-015"
title: "Memory Infrastructure (Workspace-as-Memory Pattern)"
date: "2026-02-01"
status: "Accepted"
related_to: ["ADR-013", "ADR-014"]
supersedes: []
research: "RES-OPENCLAW-001"
---

# ADR-015: Memory Infrastructure

## Context

### Prerequisites

- **ADR-013**: Established Rai is an entity (memory is constitutive)
- **ADR-014**: Defined Identity Core structure (`.rai/`)
- **RES-OPENCLAW-001**: Researched OpenClaw architecture patterns

### The Problem

Rai needs memory infrastructure that:
1. Works for **open source** (no external dependencies)
2. Scales for **commercial** (multi-user, cross-project)
3. Handles **context limits** (pre-compaction flush)
4. Provides **consistent interface** across backends

### OpenClaw Learnings

From RES-OPENCLAW-001, key patterns that work:

| Pattern | OpenClaw Implementation | Validation |
|---------|------------------------|------------|
| **Workspace-as-memory** | Markdown files as truth | 100k+ users |
| **Pre-compaction flush** | Silent memory write before truncation | Prevents data loss |
| **Two-layer memory** | Daily logs + long-term | Balances recency vs durability |
| **Truncation limits** | 20,000 chars per file | Prevents context bloat |

### Design Constraints

**Open Source (file backend)**:
- Zero external dependencies
- Git-friendly (versionable)
- Human-inspectable
- Works offline

**Commercial (database backend)**:
- Multi-user support
- Vector search (semantic)
- Cross-project patterns
- Analytics/observability

**Both**:
- Same interface (`rai memory` CLI)
- Same Identity Core structure
- Graceful degradation

## Decision

**Implement dual-backend memory infrastructure with file-first design and optional database upgrade.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Memory Interface                             │
│  rai memory status | flush | search | load | prune            │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────────┐     ┌───────────────────────────────┐
│   FileMemoryBackend       │     │   DatabaseMemoryBackend       │
│   (Open Source)           │     │   (Commercial)                │
├───────────────────────────┤     ├───────────────────────────────┤
│                           │     │                               │
│  .rai/                    │     │  PostgreSQL + pgvector        │
│  ├── memory/              │     │  ├── sessions table           │
│  │   ├── patterns.md      │     │  ├── memories table           │
│  │   ├── calibration.md   │     │  ├── embeddings               │
│  │   └── sessions/        │     │  └── relationships table      │
│  └── relationships/       │     │                               │
│                           │     │  Optional: Mem0 integration   │
│  Search: keyword (grep)   │     │  Search: vector similarity    │
│  No dependencies          │     │  Requires: PostgreSQL         │
│  Git-friendly             │     │  Multi-user ready             │
└───────────────────────────┘     └───────────────────────────────┘
```

### CLI Commands

```bash
# Status - check memory state
rai memory status
# Output:
#   Backend: file
#   Workspace: .rai/
#   Patterns: 2.3 KB (45 entries)
#   Sessions: 12 logs (7 days)
#   Last flush: 2 hours ago

# Flush - save current session state (pre-compaction)
rai memory flush [--session-id ID]
# Writes current session learnings to daily log

# Search - find in memory
rai memory search "velocity patterns"
# File: keyword search (grep)
# DB: vector similarity search

# Load - load context for session
rai memory load [--minimal | --extended | --full]
# Returns: JSON with requested context

# Prune - clean old sessions
rai memory prune --keep-days 30
# Removes session logs older than threshold
```

### File Backend Implementation

#### Structure (per ADR-014)

```
.rai/memory/
├── patterns.md      # Learned patterns (persistent)
├── calibration.md   # Velocity data (persistent)
├── insights.md      # Key insights (persistent)
└── sessions/
    ├── index.md     # Session index
    ├── 2026-02-01-identity-core.md
    ├── 2026-01-31-e2-closure.md
    └── ...
```

#### File Conventions

**Truncation limits** (prevent context bloat):
- patterns.md: 15,000 chars
- calibration.md: 5,000 chars
- insights.md: 5,000 chars
- session log: 10,000 chars each

**Daily log pattern** (like OpenClaw):
- Filename: `YYYY-MM-DD-topic.md`
- Load today's + yesterday's at session start
- Auto-prune logs older than 30 days (configurable)

**Search implementation**:
```python
def search(query: str, limit: int = 5) -> list[Memory]:
    """Keyword search across memory files."""
    results = []
    for file in memory_files:
        for line_num, line in enumerate(file.lines):
            if query.lower() in line.lower():
                results.append(Memory(
                    content=line,
                    source=f"{file.name}:{line_num}",
                    relevance=calculate_relevance(query, line)
                ))
    return sorted(results, key=lambda m: m.relevance)[:limit]
```

### Pre-Compaction Flush

**Problem**: Long sessions hit context limits; state lost on compaction.

**Solution**: Flush mechanism (inspired by OpenClaw):

```
Session tokens approach soft threshold (80% of window)
    ↓
Skill or user triggers: rai memory flush
    ↓
Current session state written to daily log
    ↓
Session continues safely (or compacts without loss)
```

**What gets flushed**:
- Decisions made this session
- Patterns discovered
- Open questions
- Progress state

**Trigger options**:
1. **Manual**: User runs `rai memory flush`
2. **Skill-triggered**: `/session-close` includes flush
3. **Checkpoint**: After feature completion, commit, etc.
4. **Future**: Auto-detect token threshold (requires agent support)

### Database Backend (Commercial)

#### Schema

```sql
-- Memories (patterns, insights)
CREATE TABLE memories (
    id UUID PRIMARY KEY,
    rai_instance_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'pattern', 'insight', 'calibration'
    content TEXT NOT NULL,
    embedding VECTOR(1536),     -- pgvector
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    rai_instance_id UUID NOT NULL,
    human_id UUID,              -- relationship link
    date DATE NOT NULL,
    topic VARCHAR(255),
    content TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP
);

-- Relationships
CREATE TABLE relationships (
    id UUID PRIMARY KEY,
    rai_instance_id UUID NOT NULL,
    human_id UUID NOT NULL,
    name VARCHAR(255),
    preferences JSONB,
    history JSONB,
    trust_level VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Search implementation

```python
async def search(query: str, limit: int = 5) -> list[Memory]:
    """Vector similarity search."""
    embedding = await embedder.embed(query)
    return await db.fetch("""
        SELECT content, source,
               1 - (embedding <-> $1) as relevance
        FROM memories
        WHERE rai_instance_id = $2
        ORDER BY embedding <-> $1
        LIMIT $3
    """, embedding, instance_id, limit)
```

### Backend Selection

```yaml
# .rai/manifest.yaml
memory:
  backend: "file"  # "file" | "database"

  # File backend settings
  file:
    truncation_limit: 15000
    session_retention_days: 30

  # Database backend settings (commercial)
  database:
    connection_string: "${RAISE_DB_URL}"
    embedding_provider: "openai"  # "openai" | "local"
```

### Interface Abstraction

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class Memory(BaseModel):
    content: str
    source: str
    timestamp: datetime
    relevance: float = 0.0

class MemoryBackend(ABC):
    """Abstract memory interface - same API, different backends."""

    @abstractmethod
    async def save_pattern(self, content: str, category: str) -> None: ...

    @abstractmethod
    async def load_patterns(self, category: str | None = None) -> list[str]: ...

    @abstractmethod
    async def save_session(self, session_id: str, content: str) -> None: ...

    @abstractmethod
    async def load_sessions(self, days: int = 2) -> list[str]: ...

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[Memory]: ...

    @abstractmethod
    async def flush(self, state: dict) -> None: ...


class FileMemoryBackend(MemoryBackend):
    """File-based implementation for open source."""
    ...

class DatabaseMemoryBackend(MemoryBackend):
    """PostgreSQL + pgvector for commercial."""
    ...
```

### Pydantic AI Integration

For session persistence, leverage Pydantic AI's upcoming features (Issue #530):

```python
from pydantic_ai import ModelMessagesTypeAdapter

# Serialize session for storage
messages_json = ModelMessagesTypeAdapter.dump_json(result.all_messages())

# Restore session
messages = ModelMessagesTypeAdapter.validate_json(messages_json)
agent.run(prompt, message_history=messages)
```

For context compression, use history_processors:

```python
from summarization_pydantic_ai import create_sliding_window_processor

agent = Agent(
    'claude-sonnet',
    history_processors=[
        create_sliding_window_processor(
            trigger=("fraction", 0.8),  # 80% of context
            keep=("messages", 50)
        )
    ]
)
```

## Consequences

### Positive ✅

1. **Zero dependencies for open source**: File backend just works
2. **Clear upgrade path**: Same interface, swap backend
3. **Pre-compaction safety**: Flush mechanism prevents data loss
4. **Git-friendly**: Memory files version-controlled
5. **Inspectable**: Human-readable markdown
6. **Scalable**: Database backend for commercial

### Negative ⚠️

1. **Two implementations**: Must maintain file + database backends
2. **Limited search (files)**: Keyword only, no semantic
3. **Manual flush**: Until auto-detection available
4. **Truncation discipline**: Users must respect limits

### Neutral 🔄

1. **Still markdown for open source**: Format doesn't change
2. **Database optional**: Not required for basic usage
3. **Pydantic AI alignment**: Uses their patterns where available

## Implementation

### E3 Scope (Revised)

| Feature | Description | Priority |
|---------|-------------|----------|
| **F3.1** | MemoryBackend interface + FileMemoryBackend | HIGH |
| **F3.2** | `rai memory` CLI commands | HIGH |
| **F3.3** | Pre-compaction flush in /session-close | HIGH |
| **F3.4** | Update /session-start to use new structure | HIGH |
| **F3.5** | DatabaseMemoryBackend (commercial) | MEDIUM |
| **F3.6** | Mem0 integration (optional) | LOW |

### Phase 1: File Backend (V2 - Feb 9)

```
F3.1: MemoryBackend + FileMemoryBackend
F3.2: rai memory status|flush|search|load|prune
F3.3: /session-close includes flush
F3.4: /session-start uses .rai/ structure
```

### Phase 2: Database Backend (V3 - Mar 14)

```
F3.5: DatabaseMemoryBackend (PostgreSQL + pgvector)
F3.6: Mem0 integration for semantic extraction
```

## Alternatives Considered

### Alternative 1: Database Only

**Rejected because**:
- Requires setup for open source
- Not inspectable
- Not git-friendly
- Violates zero-dependency goal

### Alternative 2: Mem0 Only

**Rejected because**:
- External dependency
- Overkill for single-user open source
- Can integrate later for commercial

### Alternative 3: No Flush Mechanism

**Rejected because**:
- Data loss on compaction
- OpenClaw proved this matters
- Critical for long sessions

## Validation

### File Backend Test

```bash
# Create memory
rai memory flush --content "Kata cycles deliver 2-3x velocity"

# Search memory
rai memory search "velocity"
# Expected: Returns the pattern with source

# Status check
rai memory status
# Expected: Shows file counts, last flush time
```

### Database Backend Test (Commercial)

```bash
# Same commands, different backend
export RAISE_MEMORY_BACKEND=database
export RAISE_DB_URL=postgresql://...

rai memory search "velocity patterns"
# Expected: Vector similarity results with relevance scores
```

## References

- **ADR-013**: Rai as Entity
- **ADR-014**: Identity Core Structure
- **RES-OPENCLAW-001**: OpenClaw architecture research
- **Pydantic AI Issue #530**: Message persistence
- **summarization-pydantic-ai**: Context compression

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-01 | Dual backend architecture | Open source (files) + commercial (DB) |
| 2026-02-01 | Workspace-as-memory pattern | Validated by OpenClaw (100k+ users) |
| 2026-02-01 | Pre-compaction flush | Prevents data loss (OpenClaw pattern) |
| 2026-02-01 | **Accept: Memory Infrastructure** | Complete, scalable, proven patterns |

---

**Status**: Accepted (2026-02-01)

**Approved by**: Emilio Osorio, Rai

**Impact**:
- E3 scope defined around memory infrastructure
- File backend for V2 (Feb 9)
- Database backend for V3 (Mar 14)
- CLI commands: `rai memory status|flush|search|load|prune`

**Next steps**:
1. Implement MemoryBackend interface
2. Implement FileMemoryBackend
3. Add `rai memory` CLI commands
4. Update /session-close with flush
5. Update /session-start for new structure
