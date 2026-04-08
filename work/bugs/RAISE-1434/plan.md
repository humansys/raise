# RAISE-1434: Plan

## Approach A — Remove all references

### T1: Update rai-story-close SKILL.md
- Remove "Update CLAUDE.local.md" from Step 6
- Remove CLAUDE.local.md from Output table
- Replace with: `rai session context` is authoritative (no action needed at close)

### T2: Update rai-epic-close SKILL.md
- Remove "Update CLAUDE.local.md" from Step 5
- Remove CLAUDE.local.md from Output table
- Replace with: `rai session context` is authoritative (no action needed at close)

### T3: Update rai-welcome SKILL.md
- Remove "Scaffold CLAUDE.local.md if missing" from Step 4
- Remove CLAUDE.local.md from Output table and quality checklist
- Remove from "When to skip" condition

### T4: Remove from .gitignore
- Delete the `CLAUDE.local.md` line

### T5: Commit
- Single commit with all changes
