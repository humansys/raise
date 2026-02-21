## Story Design: RAISE-235

**Summary:** Version-aware skill sync on `rai init` using dpkg three-hash algorithm.

**Research:** `work/research/skill-upgrade-strategies/` (50+ sources, HIGH confidence)

---

### Integration Decisions

#### D1: Where does the skill manifest live?

**Decision:** `.raise/manifests/skills.json` — new directory under `.raise/`.

**Rationale:** Separate from `manifest.yaml` (project metadata) because:
- Different schema, different lifecycle (skills manifest changes on every init)
- JSON not YAML — manifest is machine-managed, not human-edited
- `.raise/manifests/` directory allows future manifests (workflows, templates)

**Alternatives rejected:**
- Extend `manifest.yaml` — mixes project metadata with transient sync state
- In-frontmatter version fields — pollutes user-visible content, circular hash

#### D2: What hash algorithm?

**Decision:** SHA256 via `hashlib.sha256`.

**Rationale:** Standard, fast, collision-resistant. Same as pip, Cargo, Gentoo. No external dependency.

#### D3: What is hashed?

**Decision:** The **full file content as written to disk** (post plugin-transform). One hash per file, not per skill directory.

**Rationale:** Simple. The hash must match what was actually written, including any plugin transforms. Hashing per-file (not per-directory) means we detect changes to SKILL.md independently from references/.

**Files tracked:** Only `SKILL.md` per skill. Reference files (`references/*.md`) are always overwritten (they're framework content, not user-customizable).

#### D4: How are conflicts resolved interactively?

**Decision:** Rich prompt for TTY, skip for non-TTY.

```
rai-session-start/SKILL.md — both upstream and local changes
  [d]iff  [o]verwrite  [k]eep (default)  [b]ackup+overwrite  [O]verwrite-all  [K]eep-all
```

**Default = keep.** Yeoman's default-overwrite caused data loss (Issue #966). User work is precious.

**Rationale:** Rails Thor model, adapted. `O`/`K` (uppercase) for batch shortcuts.

#### D5: What CLI flags?

**Decision:** Three flags on `rai init`:

| Flag | Behavior |
|------|----------|
| `--dry-run` | Print table of changes, exit 0 (current) or 1 (updates available) |
| `--force` | Overwrite all skills, no prompts |
| `--skip-updates` | Keep all existing skills, only install new ones (current behavior) |

Non-TTY (piped, CI): equivalent to `--skip-updates`.

#### D6: What about reference files?

**Decision:** Reference files (`references/*.md`, `_references/*.md`) are always synced when their parent skill is updated. They are framework content, not user-customizable.

**Rationale:** Users don't customize reference files — they reference them. If the skill SKILL.md is auto-updated (user didn't touch it), references are updated too. If SKILL.md is in conflict, references follow the user's decision for the skill.

#### D7: Legacy projects (no manifest)?

**Decision:** On first `rai init` of a project without `.raise/manifests/skills.json`:
1. For each existing skill, compute SHA256 of on-disk SKILL.md
2. Compare against bundled version hash
3. If match → record as "distributed" (safe to auto-update next time)
4. If mismatch → record hash of on-disk version as "distributed" (treat as customized)
5. Install any new skills not present
6. Write manifest

**Rationale:** Conservative. Treats existing mismatched files as "customized" even if the user never touched them (could be from an older version). Safe default — worst case is a few false-positive "conflicts" on first run.

#### D8: Manifest schema

```json
{
  "schema_version": "1.0",
  "rai_cli_version": "2.1.0",
  "distributed_at": "2026-02-20T17:00:00Z",
  "skills": {
    "rai-session-start": {
      "sha256": "a1b2c3def456...",
      "version": "2.1.0",
      "origin": "framework",
      "distributed_at": "2026-02-20T17:00:00Z"
    }
  }
}
```

- `schema_version`: for forward compat
- `rai_cli_version`: which CLI version last wrote this
- `origin`: `framework` (from rai-cli package) | `org` (future: from org source)
- Per-skill `sha256`: hash of SKILL.md as written
- Per-skill `version`: from `skills_base.__version__`

#### D9: SkillScaffoldResult update

```python
class SkillScaffoldResult(BaseModel):
    skills_installed: list[str] = Field(default_factory=list)    # new skills
    skills_updated: list[str] = Field(default_factory=list)      # auto-updated
    skills_conflicted: list[str] = Field(default_factory=list)   # both changed
    skills_kept: list[str] = Field(default_factory=list)         # user chose keep
    skills_overwritten: list[str] = Field(default_factory=list)  # user chose overwrite
    skills_current: list[str] = Field(default_factory=list)      # no changes needed
    skills_skipped_names: list[str] = Field(default_factory=list)# backward compat
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    skills_copied: int = 0
    already_existed: bool = False
```

#### D10: Where in code does this live?

**Modified files:**
- `src/rai_cli/onboarding/skills.py` — core logic change (scaffold_skills + helpers)
- `src/rai_cli/cli/commands/init.py` — add `--dry-run`, `--force`, `--skip-updates` flags
- `src/rai_cli/config/paths.py` — add `MANIFESTS_DIR` constant

**New files:**
- `src/rai_cli/onboarding/skill_manifest.py` — Pydantic models + load/save for skills manifest

**Test files:**
- `tests/onboarding/test_skill_manifest.py` — manifest CRUD
- `tests/onboarding/test_skills.py` — update existing tests + new upgrade scenarios

---

### Algorithm (pseudocode)

```
def scaffold_skills(project_root, *, force=False, skip_updates=False, dry_run=False):
    manifest = load_skill_manifest(project_root) or empty_manifest()
    bundled = load_bundled_skills()
    result = SkillScaffoldResult()

    for skill_name in DISTRIBUTABLE_SKILLS:
        skill_md_path = skills_dir / skill_name / "SKILL.md"
        bundled_content = read_bundled(skill_name)
        hash_new = sha256(bundled_content)

        if not skill_md_path.exists():
            # New skill — install
            write_skill(skill_name, bundled_content)
            manifest.record(skill_name, hash_new)
            result.skills_installed.append(skill_name)
            continue

        hash_distributed = manifest.get_hash(skill_name)  # what we shipped
        hash_on_disk = sha256(skill_md_path.read())        # what's there now

        if hash_distributed is None:
            # Legacy: no manifest entry. Treat as first encounter.
            if hash_on_disk == hash_new:
                # File matches bundled — record as distributed
                manifest.record(skill_name, hash_new)
                result.skills_current.append(skill_name)
            else:
                # File differs — treat as customized
                manifest.record(skill_name, hash_on_disk)
                result.skills_current.append(skill_name)
            continue

        upstream_changed = hash_distributed != hash_new
        user_changed = hash_distributed != hash_on_disk

        if not upstream_changed and not user_changed:
            result.skills_current.append(skill_name)
        elif upstream_changed and not user_changed:
            # Safe auto-update
            if not skip_updates:
                write_skill(skill_name, bundled_content)
                manifest.record(skill_name, hash_new)
                result.skills_updated.append(skill_name)
            else:
                result.skills_current.append(skill_name)
        elif not upstream_changed and user_changed:
            # User customized, upstream didn't change — keep
            result.skills_current.append(skill_name)
        else:
            # CONFLICT: both changed
            if force:
                write_skill(skill_name, bundled_content)
                manifest.record(skill_name, hash_new)
                result.skills_overwritten.append(skill_name)
            elif skip_updates:
                result.skills_kept.append(skill_name)
            else:
                action = prompt_conflict(skill_name, skill_md_path, bundled_content)
                # handle action: keep/overwrite/backup+overwrite
                ...

    save_skill_manifest(manifest, project_root)
    return result
```

---

### Dry-Run Output Format

```
$ rai init --dry-run

Skill sync: rai-cli 2.0.0 → 2.1.0

  Skill                    Status        Action
  ──────────────────────────────────────────────────
  rai-session-start        updated       auto-update
  rai-story-plan           conflict      prompt
  rai-welcome              new           install
  rai-epic-close           current       skip
  my-custom-skill          unmanaged     skip

  Summary: 1 auto-update, 1 conflict, 1 new, 1 current, 1 unmanaged
```

---

### Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Manifest lost/corrupted | Treat as legacy project (D7) — conservative, no data loss |
| Plugin transforms change hash | Hash post-transform content — what was actually written |
| User edits manifest manually | Pydantic validation on load, graceful fallback |
| Too many conflicts on major bump | `--force` flag + dry-run preview |

---

### Backward Compatibility

- `SkillScaffoldResult` keeps old fields (`skills_copied`, `already_existed`, `files_skipped`, `skills_skipped_names`) for any callers
- First run without manifest = conservative (no data loss)
- `--skip-updates` restores exact current behavior (skip everything existing)
