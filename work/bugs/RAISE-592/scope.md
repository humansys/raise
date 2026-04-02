WHAT:      domain-model.md and system-design.md frontmatter schemas not documented in discovery skills
WHEN:      rai-discover on any project — Claude infers incorrect YAML structure
WHERE:     rai-discover, rai-discover-document, rai-project-create skills — no schema examples
           builder.py:858 — parser expects specific structure that skills don't specify
EXPECTED:  Skills include frontmatter schema with examples and pitfall warnings
Done when: Discovery skills produce valid domain-model.md and system-design.md on first try

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Design
  Qualifier:   Missing

STATUS: Valid — schema still lives only in parser code, not in skill instructions.
