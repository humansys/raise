# RAISE-1277: Autonomous mode skips LEARN step — 58% record loss

WHAT:      In autonomous mode (no HITL pauses), agent frequently skips the LEARN step in cognitive skills. E1248 reports 58% learning record loss (10 of 17 expected records missing).
WHEN:      During autonomous story execution — skills run without human pauses, agent optimizes for speed and skips the LEARN marker.
WHERE:     Skill LEARN markers in SKILL.md files (voluntary, no enforcement); no gate validates record presence.
EXPECTED:  Every cognitive skill execution produces a learning record. Missing records should be detected and flagged before story close.
Done when: Gate check validates learning record completeness before story-review/story-close. `rai gate check` reports missing records. CLI command available to check learning chain for a given work_id.

TRIAGE:
  Bug Type:    Functional
  Severity:    S1-High
  Origin:      Design
  Qualifier:   Missing
