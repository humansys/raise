WHAT:      depends_on from scanner (C# constructor injection) not wired into graph edges
WHEN:      Any graph build on a C# project with DI — deps extracted but never become edges
WHERE:     context/extractors/relationships.py:148 — _infer_depends_on only processes type='module'
           context/loaders/components.py — depends_on not passed to GraphNode metadata
EXPECTED:  Component-level depends_on produces edges in the graph
Done when: C# constructor deps appear as depends_on edges in graph output

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing

STATUS: Still valid — verified in code. _infer_depends_on skips non-module nodes (line 148).
