WHAT:      rai-story-close and rai-epic-close instruct agent to update CLAUDE.local.md
WHEN:      During story/epic close lifecycle steps
WHERE:     .claude/skills/rai-story-close/SKILL.md:144, .claude/skills/rai-epic-close/SKILL.md:176
EXPECTED:  Close skills use documented, canonical CLI sources for context capture
Done when: All CLAUDE.local.md references removed from both close skills

TRIAGE:
  Bug Type:    Configuration
  Severity:    S3-Low
  Origin:      Design
  Qualifier:   Extraneous
