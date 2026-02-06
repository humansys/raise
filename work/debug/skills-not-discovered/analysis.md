# Debug Analysis: Skills Not Discovered

## Problem Statement

**WHAT is happening:** Skills created in `.claude/skills/feature/*/SKILL.md` return "Unknown skill" when invoked via `/story-plan` or Skill tool.

**WHEN it happens:** When trying to invoke any skill created in nested directory structure.

**WHERE it occurs:** Claude Code Skill tool / slash command invocation.

**EXPECTED behavior:** Skills should be discoverable and invocable via `/skill-name`.

## 5 Whys Analysis

**Problem:** Skills in `.claude/skills/feature/plan/SKILL.md` not discovered.

1. **Why?** Claude Code's Skill tool reports "Unknown skill: story-plan"
   → Because: The skill directory doesn't exist at the expected path.

2. **Why?** The skill directory doesn't exist at expected path?
   → Because: Claude Code expects `.claude/skills/story-plan/SKILL.md` (flat), but we created `.claude/skills/feature/plan/SKILL.md` (nested).

3. **Why?** Did we use nested structure?
   → Because: We organized skills by work_cycle (feature/, tools/, project/) for logical grouping, following kata directory conventions.

4. **Why?** Does Claude Code not support nested directories?
   → Because: Claude Code skill discovery is designed for flat structure where directory name = skill name.

5. **Why?** Is this a design constraint?
   → Because: Skills are invoked by name (`/skill-name`), and the discovery mechanism maps directory names directly to invocation names.

**Root Cause:** **Directory structure mismatch** - RaiSE used nested organization (feature/plan), but Claude Code expects flat structure (story-plan).

## Ishikawa Analysis

```
                    ┌─── Method
                    │    ✓ Nested directory organization
                    │
                    ├─── Machine
                    │    ○ Claude Code discovery mechanism
                    │
SKILLS NOT          ├─── Material
DISCOVERED ◄────────┤    ✓ SKILL.md format is correct
                    │
                    ├─── Measurement
                    │    ○ No error message explaining expected path
                    │
                    ├─── Manpower
                    │    ✓ Assumption about nested support (knowledge gap)
                    │
                    └─── Milieu
                         ○ N/A
```

**Most Likely Cause:** Method (directory structure) - CONFIRMED

## Investigation Log

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| Wrong directory structure | Research Claude Code docs | Docs confirm flat structure expected | **Confirmed** |
| SKILL.md format wrong | Check frontmatter | Format is correct per spec | Eliminated |
| Size budget exceeded | Check total skill size | Not applicable - skill not found at all | Eliminated |

## Fix

**Countermeasure:** Restructure skills from nested to flat directories.

| Current (nested) | Required (flat) |
|-----------------|-----------------|
| `.claude/skills/feature/design/` | `.claude/skills/story-design/` |
| `.claude/skills/feature/plan/` | `.claude/skills/story-plan/` |
| `.claude/skills/feature/implement/` | `.claude/skills/story-implement/` |
| `.claude/skills/feature/review/` | `.claude/skills/story-review/` |
| `.claude/skills/tools/research/` | `.claude/skills/research/` |

## Prevention

1. **Documentation:** Add skill naming convention to CLAUDE.md
2. **Validation:** Could add a `raise skill validate` command to check structure

## Status

- [x] Root cause identified
- [x] Fix implemented (restructured to flat directories)
- [ ] Verified working (requires Claude Code restart)
- [ ] Prevention measures added

## Fix Applied

```bash
# Renamed nested to flat
.claude/skills/feature/design/    → .claude/skills/story-design/
.claude/skills/feature/plan/      → .claude/skills/story-plan/
.claude/skills/feature/implement/ → .claude/skills/story-implement/
.claude/skills/feature/review/    → .claude/skills/story-review/
.claude/skills/tools/research/    → .claude/skills/research/
```

## Verification

After Claude Code restart, test with:
- `/story-plan` - Should show skill content
- `/debug` - Should show debug skill
- `/research` - Should show research skill
