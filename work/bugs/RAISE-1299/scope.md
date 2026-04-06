# RAISE-1299: Scope

WHAT:      `rai skill sync` reports "All 27 skills are current" but 11 skills in skills_base/ are not in DISTRIBUTABLE_SKILLS list — never detected or deployed
WHEN:      Any project using `rai skill sync` or `rai init`
WHERE:     packages/raise-cli/src/raise_cli/skills_base/__init__.py — DISTRIBUTABLE_SKILLS list
EXPECTED:  All 38 skills in skills_base/ appear in DISTRIBUTABLE_SKILLS so sync detects and deploys them
Done when: `rai skill sync` reports all 38 skills; missing ones shown as "install"

TRIAGE:
  Bug Type:    Configuration
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
