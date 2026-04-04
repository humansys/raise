# Session Context (DEPRECATED)

> **Migrated to Claude Code native memory (2026-01-31)**

---

## New Structure

| Content | New Location | Scope |
|---------|--------------|-------|
| Working style, communication prefs | `~/.claude/CLAUDE.md` | All projects (personal) |
| Current focus, deadlines, sessions | Derived from git (ADR-038) | This project (automatic) |
| Code standards, architecture | `./CLAUDE.md` | This project (shared via git) |

---

## Why Migrate?

- **Automatic loading** — No need to manually "read context.md"
- **Proper separation** — Personal prefs don't pollute project repo
- **Native tooling** — Use `/memory` command to view/edit

---

## Session Protocol (Still Valid)

### Start
1. State session type: `kata`, `feature`, `research`, `ideation`, `maintenance`
2. State goal in one line
3. Claude automatically loads memory files

### During
- Track progress against stated goal
- Redirect if drifting (permission in personal memory)
- Tangents → `dev/parking-lot.md`

### End
1. Commit changes
2. Run `rai session close` (captures state automatically)
3. Update `dev/parking-lot.md` if new ideas captured
4. Brief wrap-up summary

---

*Deprecated: 2026-01-31*
*Session context is now derived from git automatically (ADR-038)*
