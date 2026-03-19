# Incident Report: dev Branch Merge Recovery — 2026-03-18

## Summary

Local `dev` branch had 175 unpushed commits from March 6. During the 10-day absence, a force-push from another machine rewrote the entire remote history (all SHAs changed). VS Code auto-pull triggered an unresolvable merge with ~170 conflicting files. Recovery via selective cherry-pick preserved all work from both sides.

## Timeline

| When | What |
|------|------|
| **Mar 6, 13:57** | Last shared commit: `1c68b30f` (chore: sync raise-commons) |
| **Mar 6, 13:37→** | Local work begins on this machine (e370, e493, e474, RAISE-504) — never pushed |
| **Mar 6, 20:37→** | Work continues on second machine, pushing to origin/dev |
| **Mar 6–18** | Force-push rewrites entire repo history (SHAs change, content identical) |
| **Mar 18** | Return to this machine. VS Code auto-pull → merge conflict explosion |
| **Mar 18** | Recovery session begins |

## Root Cause

A force-push from the second machine rewrote the entire git history of `origin/dev`. Evidence:

```
git reflog show origin/dev:
dca3a4c0 refs/remotes/origin/dev@{0}: pull --tags origin dev: forced-update
```

The force-push was likely part of the `sync-github.sh` filtered mirror process or a manual history cleanup. All commit SHAs changed but content was identical. Git saw the local and remote as 2926 vs 2083 completely divergent commits from the initial commit.

## Diagnosis

1. **Identified the real merge base** using `git reflog` — `1c68b30f` (Mar 6), not the initial commit
2. **Counted genuinely local commits**: 175 non-merge + 20 merge commits after the merge base
3. **Confirmed remote completeness**: all work from the second machine was pushed to origin/dev

## Recovery Strategy

1. Create safety backup: `git branch dev-local-backup`
2. Reset local dev to origin/dev: `git reset --hard origin/dev`
3. Cherry-pick 175 non-merge commits in chronological order (merge commits skipped — they were integration points only)
4. Resolve conflicts as they appeared
5. Fix integration issues post cherry-pick
6. Validate completeness

## Conflict Resolution Log

### Cherry-pick Phase (175 commits, ~12 conflicts)

#### Conflict 1: `src/raise_cli/discovery/scanner.py` (commit 6/175)
- **Cause**: Remote added `_extract_csharp_constructor_deps()` function (RAISE-227). Local s370.2 added `# noqa: C901` to the next function.
- **Resolution**: Keep both — constructor deps function + noqa annotation.
- **Applied twice** (same file, same conflict pattern).

#### Conflict 2: `pyproject.toml` + `uv.lock` (commit 16/175)
- **Cause**: Local s370.2 added `import-linter>=2.11` dependency. Remote had `mcp>=1.26,<2` in a different position.
- **Resolution**: Keep both dependencies. uv.lock taken from HEAD (regenerated later).

#### Conflict 3: `work/epics/e476-skillset-evolution/scope.md` (commit 17/175)
- **Cause**: Both sides modified epic scope. Remote had completed e476 with retrospective.
- **Resolution**: Keep remote version (more recent, contains completed work).

#### Conflict 4: `src/raise_cli/skills_base/__init__.py` (commits 29, 32/175)
- **Cause**: Local added Quality category (rai-architecture-review, rai-code-audit, rai-quality-review) to DISTRIBUTABLE_SKILLS list and docstring. Remote didn't have it.
- **Resolution**: Add Quality category to both list and docstring.

#### Conflict 5: `src/raise_cli/gates/builtin/*.py` + tests (commit 33/175)
- **Cause**: Local s474.2 refactored all 4 gate files to manifest-driven pattern. Remote had minor changes to same files.
- **Resolution**: Take local (cherry-pick) version — it was the complete refactor.

#### Conflict 6: `.raise/gates/gate-code.md` (commit 34/175)
- **Cause**: File deleted in remote, modified in local (updated for manifest-driven gates).
- **Resolution**: Keep local version (the updated documentation).

#### Conflict 7: `.raise/rai/memory/patterns.jsonl` (commits 36, 44/175)
- **Cause**: File deleted/gitignored in remote, modified in local with new patterns.
- **Resolution**: Keep local version with new pattern entries.

#### Conflict 8: `src/raise_cli/cli/commands/graph.py` (commit 75/175)
- **Cause**: Local s370.5a moved graph formatters to `output/formatters/`. Remote had minor changes.
- **Resolution**: Take local version (the extraction refactor).

#### Conflicts 9-12: Multiple `src/` files during s370.5b-c refactoring
- **Files**: `governance/extractor.py`, `parsers/epic.py`, `cli/commands/init.py`, `cli/commands/session.py`, `cli/commands/signal.py`, `cli/commands/discover.py`, `cli/commands/release.py`, `discovery/scanner.py`, `context/builder.py`, `session/bundle.py`, `cli/main.py`, `onboarding/instructions.py`
- **Cause**: Local refactoring extracted helpers, loaders, and formatters. Remote had bugfixes in same files.
- **Resolution**: Take local (cherry-pick) versions for refactored files — they contained the structural improvements.

#### Conflict 13: `README.md` (commit 126/175)
- **Cause**: Local s493.1 simplified README with installation guide. Remote had different README changes.
- **Resolution**: Take local version (the simplified README).

#### Conflict 14: `.raise/governance/code-standards-draft.md` → `code-standards.md` (commit ~168/175)
- **Cause**: Local s370.6 promoted draft to permanent. Remote had deleted the draft.
- **Resolution**: Keep local version (the promoted permanent standard).

### Post Cherry-pick Integration Fixes

After all 175 commits were applied, the following integration issues were found and fixed in a single commit (`03082173`):

#### Fix 1: Missing CLI commands in `main.py`
- **Problem**: Local refactoring of `main.py` (helper extraction) lost registration of `artifact`, `docs`, `doctor`, and `mcp` commands.
- **Fix**: Added missing imports and `app.add_typer()` calls.

#### Fix 2: Command name `adapters` → `adapter`
- **Problem**: Local refactoring changed `name="adapter"` to `name="adapters"`. Tests and CLAUDE.md reference singular form.
- **Fix**: Reverted to `name="adapter"`.

#### Fix 3: Version string `rai-cli` → `raise-cli`
- **Problem**: Local refactoring predated the package rename. Version callback still printed old name.
- **Fix**: Updated to `raise-cli version`.

#### Fix 4: `rai_cli` → `raise_cli` imports (5 files)
- **Problem**: Cherry-picked files from before the rename used old module name.
- **Files**: `cli/main.py`, `cli/commands/profile.py`, `onboarding/profile_portability.py`, + 2 test files.
- **Fix**: `sed` replacement across all 5 files.

#### Fix 5: Missing `_extract_csharp_constructor_deps` function
- **Problem**: The function was added during conflict resolution but then overwritten by a later cherry-pick (s370.5b scanner refactoring).
- **Fix**: Re-added the function definition and wired it to pass `depends_on` to Symbol constructor.

#### Fix 6: Missing `depends_on` field on Symbol model
- **Problem**: Remote RAISE-227 added `depends_on: list[str]` to Symbol. Local refactoring used the pre-RAISE-227 model.
- **Fix**: Added field to Symbol class.

#### Fix 7: Missing `_maybe_sync_skills` in `session.py`
- **Problem**: Local refactoring extracted session helpers but lost the RAISE-509 function entirely.
- **Fix**: Restored `session.py` from origin/dev (local refactoring didn't intentionally modify session commands).

#### Fix 8: Duplicate node IDs — warning vs error
- **Problem**: Remote RAISE-510 changed duplicate node IDs from warning to ValueError. Local refactored builder reverted to warning.
- **Fix**: Restored `raise ValueError` behavior.

#### Fix 9: Gitignore path patterns
- **Problem**: Remote RAISE-534 fixed path entries to not add `**/` prefix. Local refactoring reverted this.
- **Fix**: Path entries (containing `/`) now use `{entry}/**` instead of `**/{entry}/**`.

#### Fix 10: `ide.type` sync with `agents.types[0]`
- **Problem**: Remote RAISE-218 added IdeManifest sync in init command. Local refactored init didn't have it.
- **Fix**: Added `IdeManifest(type=primary)` creation and import.

#### Fix 11: String layers in architecture parser (RS-6)
- **Problem**: Remote RS-6 filtered non-dict layers. Local extracted loader didn't include this guard.
- **Fix**: Added `[layer for layer in raw_layers if isinstance(layer, dict)]` filter.

#### Fix 12: Architecture loader `.md` support
- **Problem**: Extracted loader only read `*.yaml` files. Remote builder also parsed `.md` files with YAML frontmatter.
- **Fix**: Added `.md` glob + frontmatter extraction logic.

#### Fix 13: Missing quality skill files in `skills_base/`
- **Problem**: `rai-architecture-review` and `rai-quality-review` were registered in `__init__.py` but their SKILL.md files weren't copied to skills_base.
- **Fix**: Copied from `.claude/skills/`.

#### Fix 14: `mcp_jira` test imports
- **Problem**: 3 tests imported from `raise_cli.adapters.mcp_jira` but module moved to `rai_pro.adapters.mcp_jira` in e478.
- **Fix**: Updated imports.

#### Fix 15: `patterns.jsonl` timestamp format
- **Problem**: 3 entries (PAT-E-660/661/662) had datetime timestamps with microseconds. Loader uses `date.fromisoformat()` expecting date-only strings.
- **Fix**: Converted `created` field from `2026-03-06T23:19:51.892562` to `2026-03-06`.

#### Fix 16: Stale `packages/raise-core/` directory
- **Problem**: Remote s516 moved raise-core to `src/` but empty directory remained, breaking `uv lock` (workspace member without pyproject.toml).
- **Fix**: Removed `packages/raise-core/`.

#### Fix 17: `uv.lock` regeneration
- **Problem**: Lock file was taken from HEAD during conflicts, missing new dependencies (import-linter, grimp).
- **Fix**: Ran `uv lock` to regenerate with all dependencies.

## Validation Results

| Check | Result |
|-------|--------|
| Local commits (this machine) | 174/175 present (1 empty commit skipped — metrics log only) |
| Remote commits (other machine) | 100% present |
| Key local files | 19/19 OK |
| Key remote files | 14/14 OK |
| Test suite | **3868 passed**, 0 failed, 16 skipped |

## Artifacts

- **Backup branch**: `dev-local-backup` at `b89118df` (pre-recovery state of local dev)
- **Cherry-pick list**: `/tmp/cherry-pick-list.txt` (175 commit SHAs in chronological order)
- **Integration fix commit**: `03082173` (all post-cherry-pick fixes in single commit)

## Preventive Measures

1. **Always push before leaving a machine** — unpushed work + force-push = divergence nightmare
2. **Avoid force-pushing dev** — the `sync-github.sh` script only targets the `github` remote, but whatever caused this force-push affected `origin/dev` on GitLab
3. **Investigate the force-push source** — determine exactly what caused the history rewrite to prevent recurrence
