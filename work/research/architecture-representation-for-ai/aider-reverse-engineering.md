# Aider Repo Map: Reverse Engineering Report

## Research ID: RES-ARCH-REP-001-AIDER
**Date**: 2026-02-04
**Purpose**: Decide whether to fork, adapt, or just learn from Aider's implementation

---

## Executive Summary

Aider's repo map is **well-architected and separable**. The core algorithm is:
1. Parse code with Tree-sitter → extract definitions and references
2. Build a directed graph (files as nodes, symbol references as edges)
3. Run PageRank with personalization to rank symbols
4. Binary search to fit within token budget
5. Output as formatted tree structure

**Recommendation**: **Adapt the concepts, don't fork the code.** The algorithm is straightforward, our requirements differ (unified graph integration), and a reimplementation (RepoMapper) already exists proving it's feasible.

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Aider RepoMap                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: List of files (chat files, other files, mentioned)  │
│                                                              │
│  1. PARSE (grep_ast + tree-sitter)                          │
│     └── Extract Tags: (file, line, name, kind=def|ref)      │
│                                                              │
│  2. GRAPH (networkx MultiDiGraph)                           │
│     ├── Nodes: files                                         │
│     └── Edges: symbol references (weighted)                  │
│                                                              │
│  3. RANK (PageRank + personalization)                       │
│     ├── Chat files: 50x weight                              │
│     ├── Mentioned identifiers: boosted                       │
│     └── Naming heuristics: camelCase/snake_case 10x         │
│                                                              │
│  4. BUDGET (binary search)                                  │
│     └── Fit top-ranked symbols into token limit             │
│                                                              │
│  5. FORMAT (tree structure)                                 │
│     └── file.py:                                            │
│         │class Foo:                                          │
│         ⋮...                                                 │
│         │    def bar(self):                                  │
│                                                              │
│  Output: String (formatted map within token budget)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Structures

**Tag** (namedtuple):
```python
Tag = namedtuple("Tag", "rel_fname fname line name kind")
# kind = "def" (definition) or "ref" (reference)
```

**Graph**:
- Nodes: File paths
- Edges: Weighted by reference frequency (sqrt-scaled to prevent dominance)
- Direction: From file containing reference → file containing definition

### Key Algorithm: get_ranked_tags

```python
def get_ranked_tags(self, chat_fnames, other_fnames, mentioned_fnames,
                    mentioned_idents, progress=None):
    # 1. Build definitions dict: symbol_name → list of Tags
    # 2. Build graph with files as nodes
    # 3. Add edges for each reference → definition
    # 4. Compute personalization scores:
    #    - chat_fnames: 50x weight
    #    - mentioned identifiers in paths: boosted
    #    - naming heuristics (camelCase, 8+ chars): 10x
    # 5. Run PageRank with personalization
    # 6. Distribute rank across edges to get definition ranks
    # 7. Return sorted definitions
```

### Ranking Heuristics

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Chat files | 50x | Files user is actively working on |
| Mentioned identifiers | boosted | Symbols user has referenced in conversation |
| camelCase/snake_case (≥8 chars) | 10x | Likely meaningful identifiers |
| Reference frequency | √(count) | Prevent high-frequency from dominating |

### Token Budget Algorithm

```python
# Binary search to fit within 15% of target tokens
while not close_enough:
    if too_many_tokens:
        reduce_file_count()
    else:
        increase_file_count()
```

---

## Dependencies

| Dependency | Purpose | RaiSE Alternative |
|------------|---------|-------------------|
| `grep_ast` | Tree-sitter wrapper, tag extraction | `ast-grep` (already in stack) |
| `networkx` | Graph + PageRank | Already using in unified graph |
| `diskcache` | Persistent tag cache (SQLite) | Could use, or simpler JSON cache |
| `tiktoken` | Token counting | Could use, or simple heuristic |
| `pygments` | Fallback for languages without tree-sitter refs | Optional |
| `tqdm` | Progress bars | Optional |

---

## Output Format

```
aider/coders/base_coder.py:
⋮...
│class Coder:
│    abs_fnames = None
⋮...
│    @classmethod
│    def create(
│        self,
│        main_model,
│        edit_format,
⋮...
│    def run(self, with_message=None):
⋮...

aider/commands.py:
⋮...
│class Commands:
│    voice = None
⋮...
│    def get_commands(self):
⋮...
```

**Key characteristics:**
- File path as header
- `⋮...` indicates omitted code
- `│` prefix for included lines
- Shows class/function structure with signatures
- Omits implementation details

---

## What's Separable

The RepoMapper project proves this is separable:

> "I took the RepoMap and some of its related code from aider and I fed it to an LLM...and had it create specifications for this."

RepoMapper reimplemented the concept from scratch, validating that:
1. The algorithm is understandable without Aider's codebase
2. It can be built independently
3. Works as standalone CLI or MCP server

---

## Differences from RaiSE Requirements

| Aider | RaiSE Discovery |
|-------|-----------------|
| Output: Formatted string for LLM | Output: Nodes in unified graph |
| Purpose: Context for code generation | Purpose: Component catalog + drift detection |
| Dynamic per-query | Persistent + queryable |
| Token budget focus | Graph structure focus |
| Single file output | Multiple node types (system/module/component) |

---

## Decision: Adapt, Don't Fork

### Why Not Fork Aider's Code

1. **Tight coupling**: `repomap.py` depends on Aider's caching, IO, and chat context
2. **Different output**: We need graph nodes, not formatted strings
3. **Maintenance burden**: Upstream changes would require merges
4. **License compliance**: Apache 2.0 allows it, but adds attribution requirements

### Why Not Fork RepoMapper

1. **MCP focus**: It's designed for MCP server use case, not library integration
2. **Same output issue**: Still produces formatted strings, not graph nodes

### What to Adapt

Take the **conceptual architecture**, implement for our needs:

```
Aider's Algorithm (adapt)     →    RaiSE Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tag extraction (grep_ast)     →    ast-grep (already in stack)
NetworkX graph                →    Unified graph (already exists)
PageRank ranking              →    Same algorithm, different purpose
String output                 →    ConceptNode creation
Token budget                  →    Not needed (graph has no token limit)
```

---

## Implementation Approach

### Phase 1: Extraction (like Aider's PARSE)

Use `ast-grep` to extract:
```yaml
# Symbol extraction query
rules:
  - id: extract-definitions
    pattern:
      - "class $NAME { $$$ }"       # Classes
      - "def $NAME($$$): $$$"       # Functions
      - "function $NAME($$$) { $$$ }" # JS functions
```

Output: List of symbols with file, line, name, kind

### Phase 2: Graph Building (like Aider's GRAPH)

Add to unified graph:
```python
# New node types
NodeType = Literal[..., "system", "module", "component"]

# Component node
{
    "id": "component-user-service",
    "type": "component",
    "name": "UserService",
    "kind": "class",
    "location": "src/services/user.py:15",
    "signature": "class UserService(BaseService)",
    "purpose": "",  # Filled by LLM synthesis
    "depends_on": ["BaseService", "UserRepository"]
}
```

### Phase 3: Ranking (simplified from Aider)

For Discovery, ranking serves different purpose:
- Aider: What to include in limited context
- RaiSE: What's architecturally significant

Simpler approach:
- Module-level: All top-level directories
- Component-level: Public classes/functions (exported)
- Skip internal/private by default

### Phase 4: Human Synthesis

Instead of LLM auto-generating descriptions:
1. Extract structure deterministically
2. Present to human for validation
3. Human adds/edits purpose, patterns
4. Validated data goes to graph

---

## Minimum Viable Implementation

For F&F, we need:

1. **`raise discover scan`** — Extract symbols using ast-grep
   - Input: Directory path
   - Output: JSON of symbols (file, line, name, kind)

2. **`raise discover build`** — Build component nodes
   - Input: Scan output
   - Output: Component nodes in unified graph

3. **`/discover-describe`** skill — Human synthesis
   - Rai presents extracted structure
   - Human validates and adds descriptions
   - Data saved to graph

4. **`raise context query --type component`** — Query components
   - Already have query infrastructure from E11

---

## Open Questions Resolved

| Question | Answer |
|----------|--------|
| Fork Aider? | No — adapt concepts |
| Use grep_ast? | No — use ast-grep (already in stack) |
| Use PageRank? | Maybe later — simpler heuristics for MVP |
| Token budgeting? | Not needed — graph has no token limit |
| Cache parsed tags? | Yes — but simpler than Aider's SQLite approach |

---

## References

- [Aider repo map docs](https://aider.chat/docs/repomap.html)
- [Building a better repo map](https://aider.chat/2023/10/22/repomap.html)
- [grep-ast on PyPI](https://pypi.org/project/grep-ast/)
- [RepoMapper (reimplementation)](https://github.com/pdavis68/RepoMapper)
- [ast-grep](https://ast-grep.github.io/)

---

*Research completed: 2026-02-04*
*Decision: Adapt Aider's concepts, implement for unified graph*
