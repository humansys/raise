# RES-NAMESPACE-001: Full Report

## Research Question

What naming convention should RaiSE use to namespace distributed skills so they don't collide with user-created or third-party skills in `.claude/skills/`?

## Sub-Questions

1. How does Claude Code discover and resolve skill names?
2. What are the emerging standards for skill/tool naming?
3. Is native namespacing coming to Claude Code?
4. What separator should we use?
5. What's the blast radius of renaming?

---

## Findings

### Finding 1: The Agent Skills Spec Constrains Our Options

**Confidence: VERY HIGH** (Primary source, spec text)

The Agent Skills specification (agentskills.io) — backed by Anthropic and 25+ tools — defines strict naming rules:

- Characters: `a-z`, `0-9`, `-` only
- Max 64 characters
- No leading/trailing/consecutive hyphens
- Name MUST match parent directory name
- Reserved words: `anthropic`, `claude`

**Evidence:**
1. [S1] Agent Skills spec — explicit character constraints
2. [S3] Claude Code best practices — same constraints
3. [S12] Prior research RES-SKILL-FMT-001 — confirmed Claude Code follows spec

**Impact:** This eliminates dots (`.`), colons (`:`), underscores (`_`), and double underscores (`__`) as namespace separators. The only compliant separator is the hyphen.

### Finding 2: No Native Namespacing Exists (Except Plugins)

**Confidence: HIGH** (Documentation + GitHub issues)

Claude Code provides namespace isolation only for **plugin skills** via the `plugin-name:skill-name` qualified name syntax. Project-level skills (`.claude/skills/`) exist in a flat namespace.

There is no evidence of planned user-defined namespacing in:
- Claude Code documentation
- GitHub issues (beyond plugin-related #15882)
- Agent Skills specification
- MCP specification

**Evidence:**
1. [S2] Claude Code docs — plugin namespace only
2. [S7] GitHub #15882 — plugin skills always namespaced
3. [S5] MCP SEP-993 — proposes `__` for MCP tools, not for skills

**Impact:** We must solve namespacing ourselves using naming convention.

### Finding 3: Dash-Prefix is the Only Compliant Pattern

**Confidence: HIGH** (Deductive from Finding 1)

Given the character constraint `[a-z0-9-]`, the only way to namespace is a prefix pattern using hyphens:

| Pattern | Example | Compliant? |
|---------|---------|-----------|
| `rai.session-start` | Dot separator | **No** — dots not allowed |
| `rai:session-start` | Colon separator | **No** — colons not allowed |
| `rai__session-start` | Double underscore | **No** — underscores not allowed |
| `rai-session-start` | Dash prefix | **Yes** |

The dash-prefix has a known weakness: **namespace ambiguity**. In `rai-story-implement`, is `rai` the namespace or is `rai-story` the namespace? This is a cosmetic issue, not a functional one — as long as the convention is documented.

**Evidence:**
1. [S1] Agent Skills spec — character constraint
2. [S8] npm scopes — prefix-based namespacing precedent
3. [S11] MCP servers — `<name>-mcp` prefix pattern (40% of ecosystem)

### Finding 4: Ecosystem Precedent Supports Prefix Patterns

**Confidence: HIGH** (Multiple ecosystem observations)

| Ecosystem | Pattern | Separator |
|-----------|---------|-----------|
| npm | `@org/package` | `@` + `/` |
| VS Code | `publisher.extension` | `.` |
| MCP servers | `name-mcp` or `mcp-name` | `-` |
| MCP tools (Claude Code) | `mcp__server__tool` | `__` |
| Java | `com.org.package` | `.` |

The dash-prefix pattern is the norm for ecosystems constrained to URL-safe or filename-safe characters. npm's `@scope/` and VS Code's `publisher.` are more distinctive but use characters not allowed in skill names.

### Finding 5: Blast Radius is Manageable

**Confidence: HIGH** (Codebase analysis)

The rename affects ~60 files, ~300-400 lines:

**Must update:**
- 20 skill directories × 2 locations (40 directory renames)
- 40 SKILL.md frontmatter `name:` fields
- `DISTRIBUTABLE_SKILLS` list in `src/rai_cli/skills_base/__init__.py`
- 2 methodology.yaml files (~50 references)
- 14 SKILL.md files with cross-references (Complement, Next, Previous links)
- 5 test files (~40 assertions)

**Auto-updates (no manual change):**
- MEMORY.md (regenerated from methodology.yaml)
- Graph node IDs (auto-extracted from frontmatter)

**Synchronization constraints:**
1. Directory name ↔ frontmatter `name:` must match (spec requirement)
2. DISTRIBUTABLE_SKILLS ↔ scaffolder reads this list
3. methodology.yaml ↔ MEMORY.md generation
4. Project copy of methodology.yaml synced by `/framework-sync`

**Risk level:** Medium — mechanical but many sync points. Similar to S-RENAME (554 files), but smaller scope.

### Finding 6: Collision Risk is Real

**Confidence: HIGH** (GitHub issues + client context)

Multiple Claude Code GitHub issues document naming conflicts:
- [S14] #14945, #15065, #15842 — same-name skills shadow each other

For RaiSE Jumpstart clients:
- Clients are tech leads who will create project skills
- Experienced Claude Code users may install third-party skill sets
- Generic names like `research`, `debug`, `session-start` have high collision probability
- `rai-` prefix provides sufficient distinctiveness

---

## Triangulated Claims

### Claim 1: Dash-prefix is the only spec-compliant namespace pattern

**Confidence: VERY HIGH**
1. [S1] Agent Skills spec — `[a-z0-9-]` only
2. [S3] Claude Code best practices — same constraints
3. [S4] MCP SEP-986 — LLM APIs enforce similar constraints

**Disagreement:** None. The spec is unambiguous.

### Claim 2: No native namespacing is planned for project-level skills

**Confidence: HIGH**
1. [S2] Claude Code docs — no mention
2. [S7] GitHub #15882 — only plugin namespacing discussed
3. [S10] AGENTS.md — no namespacing guidance

**Disagreement:** Absence of evidence ≠ evidence of absence. Anthropic could announce namespacing at any time. However, the Agent Skills spec's strict character constraints make it unlikely to use a new separator character.

### Claim 3: The rename is a bounded, mechanical operation

**Confidence: HIGH**
1. Codebase analysis — 60 files, 300-400 lines
2. S-RENAME precedent — 554 files completed successfully
3. PAT-253 — pre-publish is the last free rename window

**Disagreement:** PAT-151 warns "large-scale renames have a long tail." Cross-references in SKILL.md body text (not frontmatter) may be missed by simple find-replace.

---

## Recommendation

### Decision: Use `rai-` prefix for all distributed skills

**Convention:** `rai-{lifecycle}-{action}`

| Current | Namespaced |
|---------|-----------|
| `session-start` | `rai-session-start` |
| `story-implement` | `rai-story-implement` |
| `discover-scan` | `rai-discover-scan` |
| `research` | `rai-research` |
| `debug` | `rai-debug` |

**Invocation:** `/rai-session-start`, `/rai-story-implement`, etc.

### Confidence: HIGH

### Rationale

1. **Only compliant option** — Agent Skills spec eliminates all other separators
2. **Collision prevention** — `rai-` prefix is distinctive in `.claude/skills/`
3. **Ecosystem aligned** — follows MCP server naming pattern (`name-suffix`)
4. **Simple** — no aliases, no magic resolution, just a prefix convention
5. **Pre-publish window** — PAT-253 confirms this is the last free rename

### Trade-offs Accepted

1. **DX friction** — `/rai-session-start` is 4 chars longer than `/session-start`. Acceptable given collision risk with clients creating their own skills.
2. **Namespace ambiguity** — `rai-story-implement` doesn't visually distinguish prefix from name. Mitigated by consistent `rai-` prefix pattern and documentation.
3. **Not a formal namespace** — It's a naming convention, not a technical namespace boundary. If native namespacing arrives, we may need to rename again.

### Risks

1. **Native namespacing arrives with different convention** — Low probability given spec constraints. If it uses the plugin `name:skill` pattern, we'd just register `rai` as a plugin name.
2. **Rename long tail (PAT-151)** — Mitigated by thorough blast radius analysis and S-RENAME experience.
3. **Client confusion** — Mitigated by documentation and Jumpstart onboarding.

---

## Real-World Precedent: Spec Kit Ecosystem

### Finding 7: Spec Kit Validates the Dash-Prefix Pattern

**Confidence: HIGH** (Multiple implementations observed)

GitHub's Spec Kit — the most prominent skill-distributed project in the Claude Code ecosystem — went through exactly this namespace decision. Two implementations exist:

**A. Agent Skills-compliant (dceoy/speckit-agent-skills):**
Uses dash-prefix for skill directories:
- `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`
- `speckit-analyze`, `speckit-checklist`, `speckit-clarify`, `speckit-constitution`
- Symlinks from `.claude/skills/` → `../skills/` for multi-runtime support

**B. Legacy/Antigravity fork (compnew2006/Spec-Kit-Antigravity-Skills):**
Uses dot-prefix for directories:
- `speckit.specify`, `speckit.plan`, `speckit.implement`, etc.
- Placed in `.agent/skills/` (non-standard directory)
- **Not compliant** with Agent Skills spec (dots prohibited)

**C. Original Spec Kit (github/spec-kit):**
Uses dot-prefix for **legacy command files** (`.claude/commands/speckit.specify.md`) — the pre-Agent-Skills format that Claude Code still supports for backward compatibility.

**Key insight:** The ecosystem is migrating from dots to dashes. The dot convention (`speckit.specify`) originated in the legacy `.claude/commands/` format where dots were allowed in filenames. When the Agent Skills specification standardized skill naming to `[a-z0-9-]` only, compliant implementations switched to dashes (`speckit-specify`).

**Evidence:**
1. dceoy/speckit-agent-skills — dash-prefix, multi-runtime, Agent Skills compliant
2. compnew2006/Spec-Kit-Antigravity-Skills — dot-prefix, non-compliant
3. github/spec-kit — dots in legacy commands, not in Agent Skills format

**Impact:** Validates our `rai-` prefix recommendation. The most mature implementation in the ecosystem uses the identical pattern: `{namespace}-{action}`.

---

## Alternative Considered: Don't Namespace

**Status:** Rejected

**Argument:** Skills are project-local. Collision only happens if someone installs two skill sets in the same project.

**Counter-argument:** Jumpstart clients will create their own skills. Names like `research`, `debug`, `session-start` are generic enough to collide. The cost of namespacing now (pre-publish) is near-zero; the cost later (post-publish) requires migration for every installed user.

---

## Governance Link

- **Informs:** S-NAMESPACE story
- **Related:** PAT-253 (pre-publish rename window), PAT-151 (rename long tail)
- **Updates:** Parking lot item "S-NAMESPACE" — research questions answered
