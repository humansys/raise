# RAISE-634: Docs site broken links

WHAT:      Body links in docs MDX files render with `.md` extension and wrong relative paths — Starlight does not rewrite them
WHEN:      Any page visit where the user clicks a link in the body content (not sidebar)
WHERE:     docs/index.mdx, docs/cli/index.mdx, docs/concepts/index.mdx, docs/getting-started.mdx, docs/guides/create-hook.mdx, docs/guides/extending.mdx, docs/concepts/memory.mdx, docs/concepts/skills.mdx
EXPECTED:  Body links navigate to correct Starlight-generated URLs (e.g. /docs/getting-started/)
OBSERVED:  Two failure modes:
           1. .md extension not stripped → /docs/getting-started.md → 404
           2. Duplicate directory prefix → /docs/cli/cli/init.md → 404
           3. Non-existent targets → cli/README.md, concepts/README.md → 404

Done when: npm run build in site/ produces zero body hrefs with .md extension or duplicate-prefix paths
