# RAISE-504: Remove discover build and deprecated discovery skills

WHAT:      `rai discover build` writes a redundant graph to `.raise/graph/unified.json`
           using the same GraphBuilder.build() as `rai graph build`. Four deprecated
           discovery skills (start, scan, validate, document) remain in the codebase
           adding cognitive load with zero value — `/rai-discover` replaces all of them.
WHEN:      User runs `rai discover build` or sees 5 discovery skills instead of 1
WHERE:     src/raise_cli/cli/commands/discover.py:321-400 (build_command)
           .claude/skills/rai-discover-{start,scan,validate,document}/
           src/raise_cli/skills_base/rai-discover-{start,scan,validate,document}/
EXPECTED:  Single discovery skill (`/rai-discover`), no `discover build` command,
           no `unified.json` artifact.

Done when:
- [ ] `rai discover build` command removed from CLI
- [ ] Its formatter removed from output/formatters/discover.py
- [ ] 4 deprecated skill directories removed from .claude/skills/ and skills_base/
- [ ] No remaining references to removed skills or unified.json in source code
- [ ] All tests pass, linter clean, types clean
