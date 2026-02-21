# Synthesis: Skill/Template Distribution & Upgrade Strategies

**Research ID:** SKILL-UPGRADE-20260220
**Primary question:** How should `rai init` update skill files that users may have customized?

---

## Triangulated Claims

### Claim 1: The dpkg three-hash algorithm is the proven detection model

**Confidence:** HIGH

Store three values per file: (A) hash of what was originally distributed, (B) hash of file on disk now, (C) hash of new version. The decision matrix is deterministic:

| A == B (user untouched) | A == C (upstream unchanged) | Action |
|:-:|:-:|:--|
| Yes | Yes | Skip (nothing changed) |
| Yes | No | **Auto-update** (safe) |
| No | Yes | **Keep user's** (upstream didn't change) |
| No | No | **Conflict** — needs resolution |

**Evidence:**
1. **dpkg** (EC-014) — 25+ years, millions of Debian/Ubuntu systems. Very High evidence.
2. **RPM** (EC-015) — 20+ years, RHEL/Fedora/CentOS. Very High evidence.
3. **Pacman** (EC-016) — Arch Linux ecosystem. High evidence.
4. **Copier** (EC-003, EC-027) — Modern Python tool, same model. High evidence.
5. **Cruft** (EC-002) — Cookiecutter extension, same model. High evidence.

**Disagreement:** None. Universal consensus across all Linux package managers and modern scaffolding tools.

**Implication:** Use SHA256 manifest file in `.raise/` storing per-file hash at distribution time.

---

### Claim 2: Separation of framework content vs user content prevents most conflicts

**Confidence:** HIGH

The tools with the best DX avoid conflicts entirely by separating layers. User customizations never touch framework files. When customization is needed, it happens in a parallel layer (overrides, extensions) not by editing the base file.

**Evidence:**
1. **VS Code** (EC-008) — Extensions are immutable; user settings override. Very High evidence.
2. **ESLint flat config** (EC-010) — `extends` base + user `overrides`. High evidence.
3. **Helm** (EC-011) — Chart templates + user `values.yaml`. High evidence.
4. **Kustomize** (EC-012) — Base + overlay patches. High evidence.
5. **CRA** (EC-007) — Managed (zero conflicts) vs ejected (user owns). Medium evidence.

**Disagreement:** This pattern works for config/settings but has limits for content-heavy files like our skills. Skills ARE the content — you can't easily separate "framework body" from "user body" in a Markdown file.

**Implication:** Where possible, design skills so customization happens via separate files (e.g., `references/` directory, project-level overrides) rather than editing the SKILL.md itself. But we still need a conflict resolution mechanism for when users do edit SKILL.md.

---

### Claim 3: Interactive per-file prompts with diff preview is the UX gold standard

**Confidence:** HIGH

When conflicts exist, the best DX is: show each conflicting file, offer diff preview, let user decide per-file with batch shortcuts.

**Evidence:**
1. **Rails Thor** (EC-005, EC-026) — `[Ynaqdhm]` with `--pretend`/`--force`/`--skip`. Very High evidence.
2. **Yeoman** (EC-004) — `[Ynaqdhm]` prompt, but default-overwrite is controversial. High evidence.
3. **Copier** (EC-003, EC-027) — `--conflict inline` for git markers. High evidence.
4. **clig.dev** (EC-025) — Canonical CLI flag conventions. Very High evidence.

**Disagreement:** Default action is debated. Yeoman defaults to overwrite (caused data loss — Issue #966). Rails defaults to Yes. For our case, **default should be SKIP** (protect user work).

**Implication:** Implement Rails-style flags (`--dry-run`, `--force`, `--skip`) + per-file interactive prompt for conflicts. Default = skip (safe).

---

### Claim 4: A manifest file is the right storage mechanism

**Confidence:** HIGH

Store per-file metadata (hash, version, timestamp) in a single manifest file, not in the distributed files themselves.

**Evidence:**
1. **SHA256 manifest pattern** (EC-018) — Used by Cargo, npm, pip, Gentoo. Very High evidence.
2. **Cruft** (EC-002) — `.cruft.json` with template hash + context. High evidence.
3. **Copier** (EC-003) — `.copier-answers.yml` with version + answers. High evidence.
4. **Terraform** (EC-009) — `.terraform.lock.hcl` pins versions. Very High evidence.

**Disagreement:** EC-019 (frontmatter version field) argues for self-describing files. But this pollutes user content and creates circular hash problems.

**Implication:** Use `.raise/manifests/skills.json` storing per-file `{sha256, version, distributed_at}`. Keep skill files clean — no management metadata in their frontmatter.

---

### Claim 5: Dry-run mode is essential for trust

**Confidence:** HIGH

Users need to preview what will change before any mutation. This is the #1 trust-building mechanism.

**Evidence:**
1. **clig.dev** (EC-025) — Canonical recommendation. Very High evidence.
2. **Rails** (EC-005) — `--pretend` flag. Very High evidence.
3. **Copier** (EC-027) — `--pretend` flag. High evidence.
4. **gh CLI** (EC-024) — `--dry-run` flag. Very High evidence.
5. **Next.js** (EC-028) — `--dry` flag. Very High evidence.

**Disagreement:** None found.

**Implication:** `rai init --dry-run` must be a first-class feature from day one.

---

### Claim 6: Non-TTY environments should default to safe (skip) behavior

**Confidence:** HIGH

When running in CI or piped output, never prompt — default to the non-destructive option.

**Evidence:**
1. **clig.dev** (EC-025) — "If stdin is not interactive terminal, don't prompt." Very High evidence.
2. **update-notifier** (EC-023) — TTY-only notifications. Very High evidence.
3. **Supabase CLI** (EC-025 source) — `--non-interactive` flag. Medium evidence.

**Disagreement:** Some tools default to `--force` in non-TTY (dangerous). Consensus is `--skip` is safer.

**Implication:** Auto-detect TTY. Non-TTY = equivalent to `--skip`. Explicit `--force` required for destructive CI behavior.

---

## Patterns & Paradigm Shifts

### Pattern A: "Managed vs Ejected" Boundary
CRA's cautionary tale: once a user edits a managed file, they take ownership. This maps to our RAISE-235 + future ADR-038 (`rai: framework` vs `rai: custom`). The dpkg model implements this implicitly via hashing — a file with matching hash is "managed", a file with different hash is "ejected/customized".

### Pattern B: Three-Phase Update Flow
Across all tools studied, the update flow has three phases:
1. **Detect** — what changed upstream, what changed locally
2. **Decide** — auto-resolve where possible, prompt where needed
3. **Apply** — write changes, record new state

### Pattern C: Sidecar Files for Conflict Resolution
RPM `.rpmnew` and Pacman `.pacnew` patterns: when both sides changed, save the new upstream version alongside. User can diff and merge at leisure. No data loss, no forced decisions.

### Pattern D: Version-Driven Merge Strategy
SemVer for skill files (EC-031): PATCH = auto-merge safe, MINOR = merge with notification, MAJOR = require confirmation. The version delta determines the aggressiveness of the merge.

---

## Gaps & Unknowns

1. **Markdown-specific merge quality** — No tool studied does structure-aware Markdown merging. `git merge-file` is line-based. For YAML frontmatter + Markdown body, a split strategy (structured merge for frontmatter, line-based for body) would be novel but untested at scale.

2. **Sub-file customization tracking** — All tools track customization at file level. None track "user changed frontmatter but not body" or vice versa. The hybrid split strategy (EC-022 in hash catalog) is synthesized, not production-proven.

3. **Migration scripts between skill versions** — Copier and Angular support ordered migrations. No evidence of this applied to Markdown templates specifically. May be YAGNI for our case.

4. **Scale of skill file updates** — With ~24 skills, the update flow is manageable interactively. At 100+ skills, batch operations become essential. Not a concern for now but worth noting.
