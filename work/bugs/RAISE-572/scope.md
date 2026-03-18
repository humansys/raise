WHAT:      rai-story-plan genera verificaciones con paths específicos (e.g. `pyright src/module/file.py`) en lugar del comando global del manifest
WHEN:      Al planear cualquier story con archivos Python/typed
WHERE:     src/raise_cli/skills_base/rai-story-plan/SKILL.md:80 — instrucción ambigua sobre verificación
EXPECTED:  Usar `uv run pyright` (o el type_check_command del manifest) — scope global, no por archivo
Done when: La instrucción en SKILL.md prohíbe explícitamente paths específicos y exige el comando global del manifest
