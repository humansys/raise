WHAT:      Skills (epic-start, epic-close, framework-sync) instruct editing governance/backlog.md directly instead of using rai backlog CLI
WHEN:      Whenever these skills execute and reach backlog update steps
WHERE:     .claude/skills/rai-epic-start/SKILL.md, .claude/skills/rai-epic-close/SKILL.md, .claude/skills/rai-framework-sync/SKILL.md
EXPECTED:  All backlog mutations go through rai backlog CLI (create/transition/update) to keep Jira in sync
Done when: All 3 skills reference rai backlog CLI for mutations; no direct backlog.md edits for tracked work
