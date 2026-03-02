# Story Scope: rai-server Dev Documentation

> **Branch:** `story/standalone/rai-server-docs`
> **Base:** `dev`
> **Size:** M

---

## In Scope

- `rai discover scan packages/rai-server/` — extract symbols and understand the module structure
- `packages/rai-server/README.md` — dev-focused documentation covering:
  - Prerequisites (Docker, uv, Python 3.12)
  - Local setup: `docker compose up` + migrations + seed
  - Env vars (`RAI_DATABASE_URL`, `RAI_LOG_LEVEL`, `RAI_HOST`, `RAI_PORT`)
  - API reference: all endpoints with method, path, auth, request/response schema
  - Architecture: three-package structure, auth model, alembic migrations
  - Dev key and how to make authenticated requests
- Validate docs against reality by reading the actual source files

## Out of Scope

- Changes to rai-server source code
- New endpoints or schema changes
- Running the server locally as part of this story (docs only — validate by reading, not running)
- rai-core documentation → separate story if needed
- CI/CD or deployment docs → deferred

---

## Done Criteria

- [ ] `rai discover scan` run on `packages/rai-server/` — symbols extracted
- [ ] `packages/rai-server/README.md` does not exist yet (confirmed before writing)
- [ ] README created with: prerequisites, setup steps, env vars, API reference, architecture
- [ ] Every claim in the README is traceable to a source file (no guessing)
- [ ] Dev can follow README from zero to working `/health` request
- [ ] Story retrospective complete
