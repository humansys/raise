WHAT:      `ruff format --check src/ tests/` exits 1 — 51 files need reformatting
WHEN:      CI pipeline lint job; reproducible locally on dev HEAD
WHERE:     src/rai_cli/session/close.py, src/rai_cli/skills/{scaffold,schema,skillsets}.py + 47 test files
EXPECTED:  `ruff format --check` exits 0 (all files already formatted)
Done when: `uv run ruff format --check src/ tests/` exits 0 and all other gates pass
