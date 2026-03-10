# Agent Context Distribution: Evidence Catalog & Recommendations

> Research: How to distribute and safely upgrade an AI agent's configuration/context to multiple developers.
> Date: 2026-03-04
> Prior art: `work/research/rai-distribution/`, `work/research/skill-distribution/`, `work/research/multi-dev-config/`

---

## 1. Agent Context Distribution Patterns

### 1.1 The Emerging Standard: Layered Configuration

Every major AI coding tool has converged on a **three-tier layering model** for agent configuration:

| Layer | Cursor | Claude Code | Continue.dev | Windsurf | Scope |
|-------|--------|-------------|--------------|----------|-------|
| **Global/User** | User Rules (settings) | `~/.claude/CLAUDE.md` + `~/.claude/settings.json` | `~/.continue/config.yaml` | Global preferences | Per-developer |
| **Project** | `.cursor/rules/*.md` | `CLAUDE.md` + `.claude/` | `.continue/rules/` + `.continue/agents/` | `.windsurfrules` | In git, shared |
| **Organization** | Team Rules (dashboard) | (no native equivalent) | Hub rules (cloud) | (none) | Centrally managed |

**Evidence quality:** Primary (official docs for all tools)

**Sources:**
- [Cursor Rules docs](https://cursor.com/docs/context/rules) -- Team > Project > User precedence
- [Claude Code CLAUDE.md blog](https://claude.com/blog/using-claude-md-files) -- hierarchy of CLAUDE.md files
- [Continue.dev Rules docs](https://docs.continue.dev/customize/rules) -- local vs Hub rules
- [Windsurf review](https://www.secondtalent.com/resources/windsurf-review/) -- `.windsurfrules` + Memories

**Key finding:** Cursor's precedence order is **Team > Project > User** (organizational standards override personal). This is the inverse of most config systems (where local overrides global) and is deliberate -- it prevents developers from circumventing team standards.

### 1.2 "Dotfiles for AI Agents" -- The Pattern Has Arrived

Multiple practitioners have independently documented the "AI dotfiles" pattern in 2025-2026:

| Source | Approach | Distribution | Key Insight |
|--------|----------|-------------|-------------|
| [drmowinckels.io](https://drmowinckels.io/blog/2026/dotfiles-coding-agents/) | Symlink from dotfiles repo to `~/.claude/` | Git + install.sh | "A single script creates the links" |
| [Dylan Bochman](https://dylanbochman.com/blog/2026-01-25-dotfiles-for-ai-assisted-development/) | Selective symlinks, sync.sh for promotion | Git + sync/install scripts | Validate before promoting to shared |
| [Engineers Meet AI](https://engineersmeetai.substack.com/p/a-practical-guide-to-ai-dotfiles) | Bare git repo + sync script | Dual-repo (live + curated) | Physically separate secrets from shareable |
| [cutler.sg](https://cutler.sg/blog/2025-08-dotfiles-ai-coding-productivity-revolution/) | Comprehensive dotfiles | Git repo | 50-70% productivity gains claimed |

**Evidence quality:** Medium (practitioner blogs, multiple corroborating sources)

**Pattern consensus:**
1. Store AI config in a git repo (bare or standard)
2. Symlink into agent-expected locations (`~/.claude/`, `.cursor/rules/`)
3. Use install/sync scripts for setup and updates
4. Validate artifacts before promoting to shared (skills need docs, commands need format, hooks need +x)
5. Never commit secrets; use 1Password/direnv for credentials

### 1.3 Package-Distributed Configuration

Two models exist for distributing agent config through package managers:

**a) NPM/pip package ships config files** (ESLint model)
- Config lives in the package, consumed via `extends`
- User overrides locally
- Feature request exists for Cursor to read `.cursorrules` from npm packages ([forum thread](https://forum.cursor.com/t/cursor-rules-for-node-packages/82523))

**b) CLI ships config and projects it** (RaiSE model -- what we do)
- `rai init` copies skills from `rai_cli.skills_base` to `.claude/skills/`
- Uses dpkg three-hash algorithm for safe upgrades
- This is already more sophisticated than most competitors

**c) Cloud/marketplace distribution** (Continue Hub, localskills.sh)
- [localskills.sh](https://localskills.sh/blog/cursor-rules-guide) -- symlinks skills, `localskills pull` for updates
- Continue Hub -- centrally managed rules referenced via `uses:` in config.yaml

---

## 2. Safe Upgrade Patterns

### 2.1 The dpkg Three-Hash Algorithm (Already Implemented)

Our current skill sync uses this well-proven pattern from Debian package management:

```
State: (distributed_hash, current_disk_hash, new_package_hash)

Cases:
  distributed == current == new   → CURRENT (skip)
  distributed == current != new   → AUTO_UPDATE (safe to overwrite)
  distributed != current, any new → CONFLICT (user touched it)
  no distributed hash             → NEW (first install)
```

**Evidence quality:** Very High (battle-tested in dpkg for 30+ years)

This is the correct algorithm. Our implementation in `src/rai_cli/onboarding/skill_manifest.py` already does this.

### 2.2 ESLint's Shareable Config Pattern

ESLint's evolution provides a mature model for "base config + local overrides":

| Generation | Mechanism | Lesson |
|-----------|-----------|--------|
| Legacy `.eslintrc` | `extends: ["eslint:recommended", "@company/config"]` | Cascading inheritance works |
| Flat config (v9+) | `import config; export default [...config, { rules: overrides }]` | Array composition > object merge |
| 2025 `extends` return | Re-added `extends` to flat config due to user demand | Familiar patterns matter |

**Source:** [ESLint flat config extends blog](https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/)

**Key lesson:** ESLint v6 fixed a bug where shareable config overrides could incorrectly override parent config. The rule: **local config always wins over extended/base config**. This is the opposite of Cursor's team-first model, and the right choice depends on whether you're enforcing standards (team-first) or enabling customization (local-first).

### 2.3 Docker's Layer Inheritance

Docker's `FROM base AS stage` pattern maps well to agent context:

| Docker Concept | Agent Context Equivalent |
|---------------|------------------------|
| Base image | Framework-shipped identity, methodology, patterns |
| `COPY --from=base` | Selective import of framework defaults |
| Build args | Per-project or per-developer configuration |
| Multi-stage builds | Different agent profiles from same base |
| Layer caching | Only re-sync what changed |

**Key insight:** Docker's success comes from **immutable layers with explicit override points**. The base image never gets mutated; you build on top. Applied to agent context: framework-shipped files should be read-only references, with project customization happening in a separate layer.

### 2.4 chezmoi's Three-Way Merge

chezmoi performs a three-way merge between destination state, target state, and source state. This is conceptually identical to our dpkg approach but with a more interactive merge experience.

**Source:** [chezmoi merge docs](https://www.chezmoi.io/reference/commands/merge/)

**Key insight:** chezmoi uses templates with per-machine variables. This maps to our need for per-developer preferences (name, preferred patterns, experience level) applied to shared templates.

### 2.5 Upgrade Strategy Summary

| Strategy | When to Use | Risk | We Use? |
|----------|------------|------|---------|
| **Overwrite always** | Framework internals (identity, methodology) | Loses customizations | Partially (bootstrap.py skips existing) |
| **dpkg three-hash** | Skills (user may customize) | Conflict resolution UX | Yes (skill_manifest.py) |
| **Never overwrite** | User config (developer.yaml) | Stale defaults persist | Yes (bootstrap.py) |
| **Template + variables** | Per-developer adaptation of shared config | Complexity | Not yet |
| **Layered composition** | CLAUDE.md (framework base + project additions) | Ordering bugs | Not yet (single file) |

---

## 3. Multi-Developer Consistency

### 3.1 What Goes in Git vs What Gets Generated

Based on cross-tool analysis:

| Artifact | In Git? | Generated? | Rationale |
|----------|---------|-----------|-----------|
| `.raise/manifest.yaml` | Yes | By `rai init` | Project metadata, shared |
| `.raise/rai/identity/` | Yes | By `rai init` | Rai's persona, same for all devs |
| `.raise/rai/framework/` | Yes | By `rai init` | Methodology, same for all devs |
| `.raise/rai/memory/patterns.jsonl` | Yes | Accumulated | Shared learning, grows over time |
| `governance/` | Yes | Scaffolded then hand-edited | Team decisions, same for all devs |
| `.claude/skills/` | Yes | By `rai init` | Agent behavior, same for all devs |
| `CLAUDE.md` | Yes | By `rai init --detect` | Agent instructions, same for all devs |
| `~/.rai/developer.yaml` | No | By `rai init` | Personal preferences |
| `~/.claude/CLAUDE.md` | No (personal dotfiles) | By user | Personal global instructions |
| `.raise/manifests/skills.json` | Debatable | By `rai init` | Tracks distributed hashes -- should be in git for consistency |

**Key finding from AGENTS.md research:** [Blake Crosley's analysis](https://blakecrosley.com/blog/agents-md-patterns) found that "most agent files fail because they're too vague." The implication: shared agent config must be **specific and command-verifiable**, not aspirational. Every instruction should answer "what command proves this was done?"

### 3.2 Ensuring Same Agent Behavior

From the research, the reliable patterns are:

1. **Version-lock the framework** -- `rai-cli==X.Y.Z` in `pyproject.toml` ensures all devs get same skills
2. **Skills in git** -- `.claude/skills/` checked in, not generated at runtime
3. **CLAUDE.md in git** -- project instructions checked in
4. **Skill manifest in git** -- `.raise/manifests/skills.json` enables detecting drift
5. **CI gate** -- `rai init --dry-run` returns exit 1 if any skills are outdated (already implemented)

**What's missing in our current model:**
- No mechanism to enforce that all devs run `rai init` after upgrading rai-cli
- No post-install hook to auto-run `rai init` on pip install
- No CI check that skills match the pinned rai-cli version

### 3.3 Per-Developer Preferences Without Polluting Shared State

| Tool | Mechanism | Location |
|------|-----------|----------|
| Cursor | User Rules | IDE settings (not in project) |
| Claude Code | `~/.claude/CLAUDE.md` | Home directory |
| Git | `.gitconfig` | Home directory |
| ESLint | (no personal override mechanism) | N/A |

**Our current model:**
- `~/.rai/developer.yaml` -- name, experience level, projects
- `~/.claude/CLAUDE.md` -- personal Claude instructions (user manages)

**Recommendation:** This is sufficient. The key rule is: **nothing in `~/` should be required for the agent to function correctly.** Personal config should only modify tone/verbosity, never behavior.

---

## 4. Prior Art Deep-Dive

### 4.1 ESLint: Shareable Configs + Local Overrides

**Pattern:** `npm install @company/eslint-config` then `extends: ["@company"]`

| Strength | Weakness |
|----------|----------|
| Versioned via npm | Config is code (JS), not data |
| Explicit override points | Deep merge semantics are complex |
| Community ecosystem of shared configs | Migration between config formats is painful |
| `extends` composes multiple bases | No three-way merge on upgrade |

**Source:** [ESLint shareable configs](https://eslint.org/docs/latest/extend/shareable-configs)

**Applicability to RaiSE:** High. Our skills are effectively "shareable configs" distributed via pip instead of npm. The composition model (base skills + skill sets + project overrides) maps directly.

### 4.2 Docker: Base Images + Customization

**Pattern:** `FROM company/base:v2` then add project-specific layers

| Strength | Weakness |
|----------|----------|
| Immutable base layers | No merge -- only override |
| Explicit inheritance chain | Rebuilds propagate from base |
| Version tags for pinning | Size grows with layers |
| Multi-stage for variants | Complexity for simple cases |

**Applicability to RaiSE:** Medium. The "immutable base + project layer" concept is useful for identity/methodology (framework provides base, project shouldn't modify). Less useful for skills where customization is expected.

### 4.3 Dotfile Managers (chezmoi, yadm, stow)

**Pattern:** Manage home-directory config files across machines

| Tool | Merge Strategy | Template Support | Distribution |
|------|---------------|-----------------|-------------|
| **chezmoi** | Three-way merge | Go templates with machine variables | Git repo |
| **yadm** | Git-native | Jinja2 templates, alt files per host | Git repo |
| **stow** | Symlink farm | None (pure symlinks) | Git repo |

**Source:** [chezmoi docs](https://www.chezmoi.io/)

**Applicability to RaiSE:** High for the personal layer (`~/.rai/`). The template concept (same base file, different values per developer) could apply to CLAUDE.md generation where we inject project-specific values.

---

## 5. Anti-Patterns to Avoid

### 5.1 Unversioned Agent Context

**What goes wrong:**

| Symptom | Cause | Source |
|---------|-------|--------|
| "It works on my machine" for agent behavior | Skills not in git, each dev runs `rai init` against different rai-cli versions | Direct observation |
| Agent drift across sessions | Context files modified but not committed | [Agent Drift blog](https://prassanna.io/blog/agent-drift/) |
| Debugging impossible | No way to reproduce the exact context that produced a behavior | [Context Engineering, Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html) |
| Silent degradation | Framework upgrades change skills but project pins old version | Package manager experience |

**Mitigation:** Skills manifest in git + CI gate that checks `rai init --dry-run` returns 0.

### 5.2 Monolithic Config Files

**What goes wrong:**

| Symptom | Cause | Source |
|---------|-------|--------|
| Claude ignores instructions | CLAUDE.md too long (>150-200 instructions) | [Claude Code best practices](https://code.claude.com/docs/en/best-practices) |
| Merge conflicts on every PR | Single CLAUDE.md modified by everyone | Team experience |
| Contradictory rules | Rules accumulated without pruning | [AGENTS.md patterns](https://blakecrosley.com/blog/agents-md-patterns) |
| "If Claude already does it, delete the instruction" | Redundant instructions waste context budget | [HumanLayer blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md) |

**Mitigation:**
- CLAUDE.md is generated from structured sources, not hand-edited
- Skills handle domain-specific instructions (scoped, loaded on demand)
- `@import` syntax for modular composition (Claude Code supports this)

### 5.3 Auto-Updating Agent Behavior Without Consent

**What goes wrong:**

| Symptom | Cause | Source |
|---------|-------|--------|
| "The agent stopped working after update" | pip upgrade changed skills, no changelog | Package manager UX |
| Trust erosion | Agent behaves differently, developer doesn't know why | [Manus context engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) |
| Workflow breakage | New skill changes TDD flow, breaks muscle memory | Direct observation |
| Rollback impossible | No version pinning for agent context | Design gap |

**Mitigation:**
- `rai init --dry-run` to preview changes before applying
- `rai init --skip-updates` to only install new skills
- Changelog per rai-cli release documenting skill changes
- Skills manifest records which version distributed each skill

### 5.4 Vague Instructions That Produce No Behavioral Change

From [Blake Crosley's analysis of 2,500+ AGENTS.md files](https://blakecrosley.com/blog/agents-md-patterns):

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Prose without commands | "Write clean code" | "Run `ruff check .` -- must exit 0" |
| Ambiguous directives | "Be careful with X" | "Never modify X without running Y" |
| Contradictory priorities | "Move fast AND test everything" | Explicit priority ordering |
| Style without enforcement | "Use 4-space indentation" | Hook that runs formatter on save |

**Applicability:** Our CLAUDE.md is generated and mostly follows the command-first pattern. Our skills are specific. But we should audit for vague instructions periodically.

---

## 6. Recommendations for RaiSE

### 6.1 Architecture: Three-Layer Model

```
Layer 1: Framework Base (immutable, ships with rai-cli)
├── Identity (values, boundaries, principles)
├── Methodology (lifecycle, gates, patterns)
├── Base skills (rai-session-start, rai-story-*, etc.)
└── Base patterns (universal engineering patterns)

Layer 2: Project Config (in git, shared by team)
├── .raise/manifest.yaml (project metadata)
├── .raise/rai/ (projected framework base -- versioned)
├── .claude/skills/ (projected skills -- versioned via manifest)
├── CLAUDE.md (generated from structured sources)
├── governance/ (team decisions)
└── .raise/manifests/skills.json (distribution tracking)

Layer 3: Developer Personal (not in git)
├── ~/.rai/developer.yaml (preferences)
├── ~/.claude/CLAUDE.md (personal instructions)
└── ~/.claude/settings.json (Claude Code preferences)
```

### 6.2 Specific Improvements

**Priority 1: Ensure consistency across developers**
1. Commit `.raise/manifests/skills.json` to git (enables drift detection)
2. Add `rai gate check skills-current` that runs `rai init --dry-run` and fails if stale
3. Document in contributing guide: "After upgrading rai-cli, run `rai init`"

**Priority 2: Safe upgrade UX**
4. `rai init` should show a diff preview before any destructive action
5. Add `--changelog` flag to show what changed between current and new skill versions
6. Generate CLAUDE.md from structured sources (methodology.yaml + project conventions) rather than hand-editing

**Priority 3: Multi-agent support**
7. AGENTS.md generation (already started) as the cross-tool instruction file
8. Agent-specific skill transforms (already implemented via `AgentPlugin.transform_skill`)
9. Test that the same skill produces equivalent behavior across agents

**Priority 4: Future-proofing**
10. Consider a `rai upgrade` command separate from `rai init` (init = first time, upgrade = subsequent)
11. Investigate `@import` in CLAUDE.md for modular composition instead of monolithic generation
12. Template variables in skills for per-project customization (project name, test commands, etc.)

### 6.3 What NOT to Do

- Do NOT auto-run `rai init` on pip install (violates consent principle)
- Do NOT merge personal config into project config (pollutes shared state)
- Do NOT make CLAUDE.md hand-editable if it's also generated (pick one owner)
- Do NOT distribute skills outside the package (marketplace model adds complexity without solving our core problem)
- Do NOT add an "organization layer" yet (premature for current user base)

---

## Sources Index

### Primary (Official Docs, Code Inspection)
- [Cursor Rules](https://cursor.com/docs/context/rules) -- Team/Project/User hierarchy
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) -- CLAUDE.md guidelines
- [Claude Code CLAUDE.md blog](https://claude.com/blog/using-claude-md-files) -- File hierarchy and usage
- [Continue.dev Rules](https://docs.continue.dev/customize/rules) -- Local vs Hub rules
- [ESLint Shareable Configs](https://eslint.org/docs/latest/extend/shareable-configs) -- Composition pattern
- [ESLint Flat Config Extends](https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/) -- 2025 evolution
- [chezmoi merge](https://www.chezmoi.io/reference/commands/merge/) -- Three-way merge strategy
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/) -- Layer inheritance
- RaiSE codebase: `src/rai_cli/onboarding/skill_manifest.py` -- dpkg algorithm implementation
- RaiSE codebase: `src/rai_cli/cli/commands/init.py` -- current init flow

### Secondary (Analysis, Research)
- [AGENTS.md Patterns](https://blakecrosley.com/blog/agents-md-patterns) -- 2,500 repo analysis
- [Context Engineering for Coding Agents](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html) -- Martin Fowler
- [Context Engineering from Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) -- Production agent lessons
- [Agent Drift](https://prassanna.io/blog/agent-drift/) -- Failure modes in long-horizon agents
- [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) -- Practical guidelines

### Tertiary (Practitioner Blogs)
- [Dotfiles for AI Agents](https://drmowinckels.io/blog/2026/dotfiles-coding-agents/) -- Symlink + marketplace pattern
- [AI Dotfiles Guide](https://engineersmeetai.substack.com/p/a-practical-guide-to-ai-dotfiles) -- Two-tier model
- [Dotfiles for AI Development](https://dylanbochman.com/blog/2026-01-25-dotfiles-for-ai-assisted-development/) -- Sync + validate pattern
- [Claude Code Bootstrap](https://github.com/alinaqi/claude-bootstrap) -- Opinionated project init
- [Cursor Rules Guide](https://www.agentrulegen.com/guides/cursor-rules-guide) -- Complete 2026 guide
- [Reducing Context Drift](https://lumenalta.com/insights/8-tactics-to-reduce-context-drift-with-parallel-ai-agents) -- Multi-agent tactics
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) -- Anthropic official

### Prior RaiSE Research
- `work/research/rai-distribution/` -- Tool-by-tool analysis (2026-02-05)
- `work/research/skill-distribution/` -- Skill distribution design
- `work/research/multi-dev-config/` -- Multi-developer configuration patterns
