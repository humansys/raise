# Recommendation: Skill Sync on Upgrade

**Research ID:** SKILL-UPGRADE-20260220
**Decision:** RAISE-235 design

---

## Decision

**Implement the dpkg three-hash algorithm with SHA256 manifest and Rails-style interactive UX.**

**Confidence:** HIGH — 6 triangulated claims, 30+ sources, universal convergence on the core model.

---

## Architecture

### 1. Manifest File: `.raise/manifests/skills.json`

```json
{
  "schema_version": "1.0",
  "rai_cli_version": "2.1.0",
  "distributed_at": "2026-02-20T10:00:00Z",
  "skills": {
    "rai-session-start": {
      "sha256": "a1b2c3...",
      "version": "2.1.0",
      "distributed_at": "2026-02-20T10:00:00Z"
    }
  }
}
```

- Written by `scaffold_skills()` on every `rai init`
- Per-file SHA256 of the content as distributed (the "base" in 3-way terms)
- `rai_cli_version` tracks which CLI version last wrote the manifest

### 2. Detection Algorithm (dpkg model)

On `rai init`, for each skill in `DISTRIBUTABLE_SKILLS`:

```
hash_distributed = manifest.skills[name].sha256     # what we shipped last time
hash_on_disk     = sha256(skill_file_on_disk)        # what's there now
hash_new         = sha256(bundled_skill_content)      # what we'd ship now
```

| hash_distributed == hash_on_disk | hash_distributed == hash_new | State | Action |
|:-:|:-:|:--|:--|
| Yes | Yes | Current | Skip |
| Yes | No | Upstream updated | **Auto-update** |
| No | Yes | User customized | **Keep user's** |
| No | No | Conflict | **Prompt or skip** |
| (no manifest) | — | First init or legacy | **Install + record** |

### 3. Conflict Resolution UX

**Interactive mode** (TTY detected):
```
rai-session-start/SKILL.md has both upstream and local changes.
? [d]iff  [o]verwrite  [k]eep (default)  [b]ackup+overwrite  [O]verwrite-all  [K]eep-all
```

Default: **keep** (protect user work).

**Diff output:** Unified diff between user's version and new upstream version.

**Backup:** On `b`, save current as `SKILL.md.bak` before overwriting.

### 4. CLI Flags (clig.dev + Rails model)

| Flag | Behavior | Non-TTY equivalent |
|------|----------|-------------------|
| `--dry-run` | Show table of what would change, exit 0/1 | Default info mode |
| `--force` | Overwrite all files, no prompts | Must be explicit |
| `--skip` | Keep all user files, only install new skills | **Default in non-TTY** |
| (none) | Interactive per-file for conflicts | Falls back to `--skip` |

### 5. Dry-Run Output

```
$ rai init --dry-run

Skill sync: rai-cli 2.0.0 → 2.1.0

  Skill                    Status      Action
  ─────────────────────────────────────────────
  rai-session-start        updated     auto-update (unchanged by user)
  rai-story-plan           conflict    prompt (both sides changed)
  rai-epic-close           current     skip
  rai-welcome              new         install
  custom-skill             unmanaged   skip

  Summary: 1 auto-update, 1 conflict, 1 new, 21 current, 1 unmanaged
```

### 6. New Skills

Skills added in newer versions of `rai-cli` that don't exist in the project yet are installed automatically (same as today). Recorded in manifest.

### 7. Removed Skills

Skills removed from `DISTRIBUTABLE_SKILLS` in newer versions are NOT deleted from the project. They become "unmanaged" — not tracked in manifest anymore.

---

## Rationale

1. **dpkg model** — 25+ years, millions of systems, universal consensus across all package managers. Not a single source disagreed. (Claims 1, 4)
2. **SHA256 manifest** — External to skill files, clean separation. No metadata pollution in user-visible content. (Claim 4)
3. **Rails interactive UX** — Gold standard for per-file conflict resolution. 20+ years of refinement. (Claim 3)
4. **Default=keep** — Yeoman's default-overwrite caused data loss (Issue #966). User customizations are precious. (Claim 3)
5. **Dry-run first** — Universal recommendation across all ecosystems. Essential for trust. (Claim 5)
6. **Non-TTY=skip** — clig.dev canonical guidance. CI safety. (Claim 6)

---

## Trade-offs

| Accepting | Over |
|-----------|------|
| File-level detection (atomic) | Sub-file awareness (frontmatter vs body) |
| External manifest | Self-describing files (frontmatter metadata) |
| Simple keep/overwrite conflict resolution | 3-way merge with `git merge-file` |
| No migration scripts | Ordered transforms between versions |

**Why these trade-offs:** Phase 1 simplicity. The dpkg model covers 90%+ of cases. The 10% edge case (both sides changed) is handled by keep+manual review, which is safe if not optimal. Phase 2 can add 3-way merge and sub-file awareness.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Manifest file lost/corrupted | Low | Medium (all files appear "customized") | Treat missing manifest as first-init: hash all existing files, install only new ones |
| User doesn't know about `rai init` after upgrade | Medium | Low (stale skills, not broken) | Print notice on any `rai` command when version drift detected |
| Too many conflicts on major version bump | Low | Medium (tedious prompts) | `--force` flag + dry-run preview |
| Manifest schema evolves | Low | Low | `schema_version` field for forward compat |

---

## Alternatives Considered

### A: Copier-style 3-way merge
- **Why not:** Requires storing full base file content (not just hash) — heavier. `git merge-file` dependency. More complex implementation. Only benefits the "both changed" case which is rare for skill files.
- **When to adopt:** Phase 2, if users frequently customize AND we frequently update the same skills.

### B: Frontmatter version field (self-describing)
- **Why not:** Pollutes user-visible content. Circular hash problem. Mixing concerns.
- **When to adopt:** Never for management metadata. Version in frontmatter is fine for human info but shouldn't drive the sync mechanism.

### C: Layer separation (ESLint extends model)
- **Why not:** Skills are content, not config. Can't easily split into "base layer" and "override layer" for Markdown prose.
- **When to adopt:** Already partially implemented via `references/` subdirectory. Could evolve post-ADR-038.

### D: RPM `.rpmnew` sidecar pattern
- **Why not now:** Interactive prompt is better UX for our small file count (~24). Sidecar files accumulate and need cleanup tooling.
- **When to adopt:** If we add `--non-interactive` mode that doesn't skip conflicts, save new version as `.rai-new` for later review.

---

## Implementation Scope for RAISE-235

1. **Manifest creation** — `scaffold_skills()` writes `.raise/manifests/skills.json` after distributing
2. **Detection logic** — Three-hash comparison on each `rai init`
3. **Auto-update path** — Overwrite unchanged files silently, update manifest
4. **Conflict handling** — Interactive prompt (keep/overwrite/diff/backup) for TTY, skip for non-TTY
5. **CLI flags** — `--dry-run`, `--force`, `--skip`
6. **Legacy handling** — First init on existing project without manifest: hash all files, install only new skills
7. **`SkillScaffoldResult` update** — Report updated/conflicted/new/skipped skills
8. **Tests** — Upgrade scenario, conflict scenario, dry-run, force, skip, non-TTY, legacy

---

## Governance Linkage

- **Informs:** RAISE-235 story design
- **Future:** ADR-038 (skill ownership semantics) can layer on top of this manifest
- **Parking lot:** `rai skill diff` command (RPM `pacdiff` equivalent) — deferred
