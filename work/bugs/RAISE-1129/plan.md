# RAISE-1129: Plan

## Context

`docs/` tiene contenido .mdx (sin componentes JSX — solo frontmatter + markdown).
Necesitamos publicarlo como sitio standalone en `docs.raiseframework.ai` via
Cloudflare Pages. Usamos MkDocs + Material como generador.

## Tasks

### T1: Bootstrap MkDocs — mkdocs.yml + dependencias
- Crear `mkdocs.yml` en raíz con Material theme, nav basada en el sidebar actual de Starlight
- Agregar mkdocs-material como dev dependency en pyproject.toml
- Renombrar .mdx → .md en docs/, limpiar frontmatter Starlight → MkDocs
- Verify: `uv run mkdocs build --strict` pasa sin errores
- Commit: `fix(RAISE-1129): bootstrap MkDocs site from existing docs content`

### T2: Create deploy-docs.yml workflow
- GitHub Actions: build MkDocs, deploy a Cloudflare Pages proyecto `raise-docs`
- Triggers: push to main on paths `docs/**` y `mkdocs.yml`, plus workflow_dispatch
- Verify: YAML es válido, all code gates pass
- Commit: `fix(RAISE-1129): add deploy-docs.yml for docs.raiseframework.ai`

### Manual steps (post-merge, by Emilio)
- Crear Cloudflare Pages project `raise-docs`
- Añadir custom domain `docs.raiseframework.ai`
- Verificar GitHub secrets CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID
- Trigger workflow_dispatch para primer deploy
