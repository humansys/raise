---
type: module
name: docs-site
purpose: "MkDocs-based documentation site — docs.raiseframework.ai"
status: current
depends_on: []
depended_by: []
entry_points:
  - "uv run mkdocs build --strict"
  - "uv run mkdocs serve"
public_api: []
components: 3
constraints:
  - "Zero npm dependencies — Python-only build pipeline"
  - "Content lives in docs/ as plain .md files"
  - "Deploy is automated via GitHub Actions on push to main"
---

## Purpose

Static documentation site for the RaiSE framework, served at `docs.raiseframework.ai`. Built with **MkDocs + Material for MkDocs** — a Python-based static site generator with minimal dependency surface and zero CVE churn from JS transitive deps.

Replaces the previous Astro + Starlight setup (removed in RAISE-1129) which generated continuous security alerts from its JS dependency tree (picomatch, rollup, yaml, etc.) for a use case that only needs markdown → HTML.

## Architecture

```
docs/                     Content (plain .md, frontmatter: title + description)
├── index.md              Home page
├── getting-started.md
├── installation.md
├── concepts/             Core concepts (memory, skills, governance, knowledge graph)
├── guides/               How-to guides (first story, adapters, hooks, etc.)
├── cli/                  CLI reference (one page per command group)
├── es/                   Spanish translations (partial)
└── assets/               Images and static files

mkdocs.yml                Site configuration (theme, nav, extensions)
_site/                    Build output (gitignored)
```

## Build & Deploy

### Local development

```bash
uv run mkdocs serve          # http://127.0.0.1:8000 with hot reload
uv run mkdocs build --strict # Build to _site/, fail on broken links
```

### CI/CD

**Workflow:** `.github/workflows/deploy-docs.yml`

```
push to main (docs/** or mkdocs.yml changed)
    → uv sync --group dev
    → mkdocs build --strict
    → wrangler pages deploy _site --project-name=raise-docs
```

**Infrastructure:**
- **Host:** Cloudflare Pages, project `raise-docs`
- **Domain:** `docs.raiseframework.ai`
- **Secrets:** `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` (GitHub repo secrets)
- **Trigger:** push to `main` on `docs/**` or `mkdocs.yml`, plus `workflow_dispatch`

### Adding content

1. Create/edit `.md` files in `docs/`
2. Add to `nav:` section in `mkdocs.yml` if it's a new page
3. Use relative links between pages (e.g., `../concepts/memory.md`)
4. Push to main — deploy is automatic

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| MkDocs over Astro | Zero npm deps, no JS CVE surface, Python-native (already in stack) |
| Material theme | De facto standard for Python framework docs (FastAPI, Pydantic, Ruff) |
| `--strict` flag | Broken links fail the build — prevents silent 404s |
| Cloudflare Pages | Already used for raise-gtm, consistent infra |
| No versioning (yet) | Single version sufficient until v3.0 breaking changes (RAISE-944) |

## History

- **Pre-2026-03-30:** Documentation was embedded in `site/` (Astro + Starlight), deployed as part of `raise-gtm` Cloudflare project. Links broke when site/docs were separated (RAISE-634).
- **2026-03-30 (RAISE-1129):** Astro removed, MkDocs bootstrapped, independent deploy to `raise-docs` Cloudflare project. Covers epic RAISE-823 stories S823.1–S823.5.
- **Future (v3.0):** Versioned docs via `mike` plugin (RAISE-944).
