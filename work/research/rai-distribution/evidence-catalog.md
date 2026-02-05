# Evidence Catalog: Rai Distribution Research

> All evidence sources with quality ratings.

**Research ID:** RES-RAI-DIST-001
**Date:** 2026-02-05

---

## Evidence Rating Scale

| Rating | Description | Reliability |
|--------|-------------|-------------|
| **Primary** | Direct code/config inspection | Very High |
| **Secondary** | Official documentation | High |
| **Tertiary** | Community reports, blogs | Medium |

---

## Tool Research Evidence

### OpenClaw

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Identity files | Primary | GitHub repo | SOUL.md, IDENTITY.md, AGENTS.md, USER.md |
| System prompt assembly | Primary | Code inspection | Dynamic prompt building |
| Onboarding wizard | Primary | CLI code | `openclaw onboard --install-daemon` |
| Self-bootstrapping | Primary | Code | Agent reads own workspace files |

**File:** `tools/openclaw.md`

### Aider

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| System prompts | Primary | `aider/coders/*_prompts.py` | Hardcoded functional roles |
| `/help` mode | Primary | Code | "You are an expert on Aider" |
| CONVENTIONS.md | Primary | Code | Read-only context loading |
| Issue #1258 | Tertiary | GitHub Issues | User demand for identity customization |
| Repo map | Primary | Code | Tree-sitter + graph ranking |

**File:** `tools/aider.md`

### Continue.dev

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Config schema | Primary | Code | baseSystemMessage, rules files |
| First-run detection | Primary | Code | `hasBeenInstalled` flag |
| Tool serialization | Primary | Code | Runtime capability injection |
| No persona | Primary | Code inspection | Blank slate design |

**File:** `tools/continue-dev.md`

### Cline

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| System prompt | Primary | Code | "Highly skilled software engineer" |
| .clinerules/ | Primary | Code | v3.7+ directory pattern |
| Plan/Act modes | Primary | Code | Read-only plan, controlled act |
| Memory Bank | Tertiary | Community | Methodology, not built-in |
| Tool definitions | Primary | Code | What/when/how in prompt |

**File:** `tools/cline.md`

### Mentat

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| No personality | Primary | Code | Purely functional |
| Hidden prompts | Tertiary | Third-party interception | `no_parser_prompt` setting |
| ChromaDB | Primary | Code | Project context only |
| Archived status | Secondary | GitHub | CLI archived Jan 2025 |

**File:** `tools/mentat.md`

### Cursor

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Rules system | Secondary | Documentation | User → Project → Legacy |
| .mdc format | Secondary | Docs | YAML frontmatter + markdown |
| No self-knowledge | Secondary | Docs | Features via UI, not AI |
| First-run wizard | Tertiary | User reports | Theme/keymap only |

**File:** `tools/cursor.md`

### GitHub Copilot

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Custom Instructions | Secondary | Documentation | .github/copilot-instructions.md |
| Agent Skills | Secondary | Docs | Folders auto-loaded |
| No personality | Secondary | Docs | Deliberately neutral |
| Frictionless onboard | Secondary | Docs | One-click enable |
| MCP integration | Secondary | Docs | Standard tool discovery |

**File:** `tools/copilot.md`

---

## Team Memory Research Evidence

### Cursor Business/Teams

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Team rules | Secondary | Documentation | Dashboard-managed |
| Per-project memory | Tertiary | Community | Not cross-project |

### Copilot Enterprise

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Copilot Spaces | Secondary | Documentation | Curated context sharing |
| Org instructions | Secondary | Docs | Organization-level |
| No pattern learning | Secondary | Docs | Context, not learning |

### Letta (MemGPT)

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Architecture | Primary | Documentation | Core + Archival memory |
| Self-editing | Primary | Docs | Agent modifies own memory |
| XML blocks | Primary | Code | Structured memory format |

### LangMem

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Namespace model | Secondary | Documentation | (org, team, user, type) |
| Memory types | Secondary | Docs | Semantic, Episodic, Procedural |
| LangGraph integration | Secondary | Docs | Native support |

### ICML 2025

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| Private/Shared tiers | Secondary | Paper | Two-tier architecture |
| Provenance | Secondary | Paper | Attribution tracking |
| Access graphs | Secondary | Paper | Bipartite permission model |

**File:** `tools/team-memory-patterns.md`

---

## Internal Evidence

| Evidence | Type | Source | Finding |
|----------|------|--------|---------|
| PAT-095 | Internal | patterns.jsonl | Base Rai needs framework knowledge |
| ADR-013 | Internal | decisions/ | Rai as Entity architecture |
| E7 completion | Internal | Session history | Onboarding infra ready |
| V3 requirement | Internal | Stakeholder | Team sync is hard requirement |

---

## Evidence Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No tool has team learning | Can't copy pattern | Design from principles |
| Tabnine closed | Can't inspect | Rely on docs |
| Cursor closed | Can't inspect internals | Docs + community |
| Long-term success data | Unknown what works | Start simple, iterate |

---

## Triangulation Summary

### Claim: No tool has named personality

| Source 1 | Source 2 | Source 3 | Confidence |
|----------|----------|----------|------------|
| OpenClaw code (blank) | Aider code (functional) | Cursor docs (anonymous) | Very High |

### Claim: Memory is a gap

| Source 1 | Source 2 | Source 3 | Confidence |
|----------|----------|----------|------------|
| Cline (community Memory Bank) | Aider (none) | Continue (none) | Very High |

### Claim: Team learning is unsolved

| Source 1 | Source 2 | Source 3 | Confidence |
|----------|----------|----------|------------|
| Cursor Teams (rules only) | Copilot Enterprise (context only) | Tabnine (model-level) | High |

---

*Compiled: 2026-02-05*
