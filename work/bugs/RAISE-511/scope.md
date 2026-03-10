# RAISE-511: Docs site shows wrong install command

WHAT:      Install commands in the public docs site reference `rai-cli` instead of `raise-cli`
WHEN:      Any user visits raiseframework.ai/docs/ and follows the install instructions
WHERE:
  - docs/src/content/docs/docs/getting-started.mdx (lines 39, 46, 49, 60)
  - docs/src/content/docs/docs/index.mdx (line 20)
  - docs/src/content/docs/es/docs/getting-started.mdx (line 31)
  - docs/src/content/docs/es/docs/index.mdx (line 20)
EXPECTED:  All install commands reference `raise-cli` (the correct PyPI package name)
Done when: All 4 files show `raise-cli` in every install code block; no `rai-cli` remains in docs/src/
