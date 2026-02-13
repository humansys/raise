# Retrospective: S18.5 — GitHub Organization Setup

## Summary
- **Story:** S18.5
- **Size:** M (estimated 60 min)
- **Started:** 2026-02-13 15:37
- **Completed:** 2026-02-13 16:15
- **Actual:** ~38 min
- **Velocity:** 1.58x

## What Was Delivered

- `humansys/raise` private repo with description, topics, homepage
- `engineering` team with 4 members (oemilio, emilio-humansys, aquilesHs, danieloliva-humansys)
- 16 labels (9 default + 7 custom for scope/priority)
- `scripts/sync-github.sh` — orphan-commit filtered mirror script
- `.github/pull_request_template.md`
- Clean public content: `src/`, `tests/`, `framework/`, root community files only

## What Went Well

- **gh CLI integration worked smoothly** — all org/repo/team/label operations done programmatically via API
- **Orphan commit approach is clean** — no history leakage, idempotent, single commit on public side
- **Iterative exclusion list was caught early** — blog/, docs/, governance/, .claude/, scripts/ discovered through review before public exposure
- **Quick recovery from script crash** — force checkout + fix + re-sync in one iteration

## What Could Improve

- **Sync script wasn't tested with gitignored files** — `CLAUDE.local.md` is in `.gitignore` so it never exists on checkout branches, but the script assumed `[ -f "$file" ]` would catch it. Should have used `git rm --ignore-unmatch` from the start.
- **Design doc drifted from reality** — design still lists `governance/` and `.claude/` as "Included" even though they were later excluded. Design should have been updated with each exclusion decision.
- **Branch protection deferred** — GitHub Free org doesn't support branch protection on private repos. Not a miss in execution, but a gap in plan risk assessment.

## Heutagogical Checkpoint

### What did you learn?
- `git rm -f` fails on files not in the index even with `-f`. `--ignore-unmatch` is the correct flag for "remove if tracked, skip if not".
- GitHub Free org plan has real limitations: no branch protection on private repos, limited team features. Upgrading to Team ($4/user/mo) or making the repo public unlocks these.
- Orphan commits are the right pattern for "show current state, no history" mirrors.

### What would you change about the process?
- **Test the sync script against all exclusion targets** before the first real push. A dry-run mode (`--dry-run`) would have caught the CLAUDE.local.md issue.
- **Update design doc when decisions change** — the exclusion list evolved 3 times (blog/docs added, then governance/.claude/scripts added) but design.md wasn't updated to match.

### Are there improvements for the framework?
- Scripts that manipulate git branches should always use `--ignore-unmatch` for removals — defensively assume files may not exist.
- A `--dry-run` flag on sync scripts prevents surprises on first real execution.

### What are you more capable of now?
- GitHub org administration via `gh` CLI API calls (teams, permissions, labels, repo config)
- Filtered mirror strategies with orphan commits
- Recovering from git state corruption during script failures

## Improvements Applied

- Sync script now uses `--ignore-unmatch` (committed: c175711)
- Directory existence check uses `git ls-files --error-unmatch` instead of filesystem check

## Done Criteria Status

| Criteria | Status | Notes |
|----------|--------|-------|
| `humansys/raise` repo exists | DONE | Private (public on launch day) |
| Teams configured | DONE | engineering team, 4 members, write access |
| Branch protection on main | DEFERRED | Requires public repo or paid plan |
| Issue templates | SKIPPED | Not critical for private phase |
| Labels created | DONE | 16 labels |
| Open-core code pushed | DONE | Filtered orphan commit, clean content |
| README links to correct repo | PENDING | Will update when repo goes public |

## Action Items
- [ ] Update design.md exclusion lists to match final state
- [ ] Add `--dry-run` flag to sync-github.sh (future enhancement)
- [ ] Enable branch protection when repo goes public
- [ ] Update README links to point to github.com/humansys/raise
