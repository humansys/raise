# RAISE-634: Analysis

## 5 Whys

1. Body links give 404 → hrefs in built HTML have `.md` extension and duplicate directory prefixes
2. → MDX source files use relative links like `getting-started.md`, `cli/init.md` — Starlight does not rewrite body content links
3. → Files were written assuming a flat collection (`src/content/docs/getting-started.mdx`)
4. → RAISE-514 introduced symlink `src/content/docs/docs → ../../../../docs`, nesting content one level deeper — links were not updated
5. → No automated link checking in the build pipeline to catch broken hrefs in generated HTML

## Root Cause

The single-source architecture migration (RAISE-514) changed the depth of content files in the
collection but body links were not updated. Starlight generates correct URLs for sidebar items
(using slug config), but does not rewrite relative `.md` hrefs in MDX body content.

## Fix Approach

Replace all body links in docs MDX files with absolute paths (`/docs/...`) without `.md` extension.
Absolute paths are independent of collection depth and resilient to future structural changes.

Files affected:
- docs/index.mdx
- docs/getting-started.mdx
- docs/cli/index.mdx
- docs/concepts/index.mdx
- docs/concepts/memory.mdx
- docs/concepts/skills.mdx
- docs/guides/create-hook.mdx
- docs/guides/extending.mdx
