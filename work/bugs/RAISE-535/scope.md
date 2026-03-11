# RAISE-535: Identical if-branch bodies in context/analyzers/python.py

WHAT:      if/else branches at line 91 execute identical code — condition is dead
WHEN:      When analyzing module imports in `_analyze_module()`
WHERE:     src/raise_cli/context/analyzers/python.py:91-97
EXPECTED:  Either branches do different things or the if/else is collapsed
Done when: Dead condition removed, behavior preserved, regression test confirms
