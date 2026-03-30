# Session Diary: E1051 — Confluence Adapter v2

**Date:** 2026-03-29 / 2026-03-30 (overnight session)
**Type:** Epic implementation — 7 stories in one session
**Branch:** `worktree-epic-raise-1021` → merged to `release/2.4.0`
**Participants:** Emilio Osorio, Rai

---

## La Misión

Reemplazar la integración de Confluence basada en MCP + Node (mcp-atlassian) por un adapter puro Python. El driver: cada invocación de MCP spawneaba un subprocess de Node, limitaba a 5 de 11 funciones, y el debugging era opaco. Queríamos control total, visibilidad total, cero dependencias externas al ecosistema Python.

Pero durante el diseño, la misión creció. No solo queríamos un adapter — queríamos que **cada skill del framework publicara automáticamente a Confluence**. Que la documentación de proyecto dejara de ser un afterthought y fuera un side-effect natural del proceso de desarrollo.

---

## Decisiones Arquitectónicas Clave

### 1. "¿Dónde vive el adapter?"

**Decisión:** En `raise-cli` (open-core), no en `raise-pro`.

Emilio lo planteó claro: "para reducir fricción con nuestro target primario (usuarios de Jira/Confluence), los conectores de Atlassian deben estar en la versión comunitaria." Esto significa que cualquiera que instale `raise-cli[confluence]` tiene el adapter completo. Sin licencia, sin pro.

### 2. "¿Construimos rate limiter?"

**Decisión:** No. `backoff_and_retry=True`.

Investigué `atlassian-python-api` antes de escribir código. La librería tiene backoff exponencial + jitter + respeto a `Retry-After` header, con 5 reintentos configurables. El `JiraClient` existente en el proyecto tenía un `RateLimiter` manual con sliding window — innecesario cuando la librería lo hace nativamente. YAGNI puro.

### 3. "¿4 excepciones o 3?"

**Decisión:** 3 clases. Dropped `ConfluenceRateLimitError`.

Si la librería maneja 429 automáticamente con retries, un post-retry failure es simplemente un `ConfluenceApiError`. El caller no necesita distinguir "falló por rate limit" de "falló por otra razón" — en ambos casos, el retry ya se intentó. Esto es YAGNI aplicado a error hierarchy.

### 4. "¿Permisivo o estricto en publish?"

**Decisión:** Estricto. Require routing + parent page.

Esto surgió en el Architecture Review. Mi primera implementación era permisiva: si no había routing, publicaba como root-level page. Emilio corrigió: "somos reliable, recuerda." Cambié a: sin routing configurado → rechaza. Parent page no existe → rechaza con mensaje claro. El filesystem siempre escribe (durabilidad), pero Confluence solo acepta cuando todo está configurado correctamente.

### 5. "¿Un adapter o dos?"

Esta fue la conversación más interesante del epic. Empezamos con `PythonApiConfluenceAdapter` que implementa `DocumentationTarget`. Luego Emilio preguntó: "quiero que los skills ya no escriban a filesystem, solo al adapter."

Pero el filesystem es valioso (offline, git history, context para Claude). Y Confluence es el source of truth remoto. ¿Cómo hacer ambos con un solo path?

**Decisión:** `CompositeDocTarget` — un target que wrappea N targets y publica a todos.

```
skill → rai docs publish → CompositeDocTarget
                            ├→ FilesystemDocsTarget (local)
                            └→ ConfluenceAdapter (remoto)
```

El resolver auto-compone cuando encuentra 2+ targets registrados. Sin flags, sin config adicional. Instala `raise-cli[confluence]` y automáticamente tienes dual-write.

### 6. "¿Quién va primero en el composite?"

**Decisión:** Filesystem primero, Confluence último.

Filesystem nunca falla. Es tu garantía de durabilidad. Confluence puede estar caído, puede haber un error de auth, puede timeout. Si Confluence falla pero filesystem escribió, el resultado es `success=True` con warning "sync pending". El archivo local es la prueba de que el contenido existe.

La URL retornada viene del último target exitoso (Confluence si funcionó, filesystem path si no). Así el usuario ve la URL útil sin sacrificar confiabilidad.

### 7. "¿Los skills usan Write tool o el adapter?"

**Decisión:** Solo el adapter. `--stdin` + `--path`.

Emilio insistió: "los skills SIEMPRE deben ir al adapter de docs." Primero implementé Write + `--file` (dos pasos). Emilio preguntó: "¿pero no que estábamos haciendo que una sola llamada al adapter hiciese el write a filesystem y la escritura a Confluence?" Tenía razón.

Agregamos `--stdin` y `--path` al CLI. Los skills ahora pasan contenido via heredoc:

```bash
rai docs publish story-design --stdin \
  --path work/epics/.../design.md \
  --title "S1.1 Design" <<'EOF'
# Design content
EOF
```

Un solo comando. El adapter escribe a ambos destinos. El skill nunca toca el Write tool para artefactos.

---

## El Prerrequisito Inesperado: RAISE-1060

Antes de construir el adapter, evaluamos `models.py` contra la visión de adapters. Encontramos 4 concerns mezclados en un solo archivo + internals del filesystem adapter leaking al módulo público. Creamos RAISE-1060 (models restructure) como prerrequisito: monolítico `models.py` → paquete `models/` con submódulos (pm, docs, governance, health) + re-export via `__init__.py` para zero breaking changes.

Emilio dijo: "preferiría hacer primero esa épica, dejar el terreno limpio y construir sobre una base sólida." Y así lo hicimos. Cero ventanas rotas.

---

## Patrones Descubiertos

### PAT: `backoff_and_retry` built-in
No construyas rate limiters cuando la librería los tiene. Verifica antes de implementar.

### PAT: `get_page_by_title` returns `None` OR `{}`
La librería de Atlassian devuelve falsy values diversos. Siempre usar `if not result:`, nunca `if result is None:`.

### PAT: `set_page_label` es aditivo
Para semántica de "replace labels", necesitas: get existing → diff → remove + add. La API solo agrega.

### PAT: Typed exceptions via `isinstance`
`atlassian.errors` tiene `ApiPermissionError`, `ApiNotFoundError`, `ApiError`. Usa `isinstance`, no string matching.

### PAT: Identity en env vars, config compartida
Config files (.yaml) son compartidos en el repo. Identity (username, token) en env vars personales. Nunca PII en config trackeado.

---

## Métricas

| Metric | Value |
|--------|-------|
| Stories completadas | 7 de 10 (3 deferred a v2.5.0) |
| Tests nuevos | ~80 (suite total: 3781) |
| LOC src nuevos | ~450 |
| LOC test nuevos | ~900 |
| Skills actualizados | 14 (4 story + 4 epic + 6 operacionales) |
| Routing types configurados | 18 |
| Artefactos publicados a Confluence | 32 (dogfood del propio epic) |
| E2E tests contra Confluence live | 9/9 adapter + 11/11 client |
| Bugs encontrados en QR | 3 (set_labels semántica, empty dict, expand gap) |
| AR questions answered | 4 (KeyError vs custom, heurística flat, result ordering, strict publish) |

## Timeline

| Hora (aprox) | Actividad |
|---|---|
| Inicio | Session start, retomar E1051 desde S1051.1 completado |
| +30min | S1051.3 Config schema — 22 tests, QR encontró empty YAML guard |
| +1h | S1051.2 Adapter — 16 tests, AR encontró permissive defaults → strict fix |
| +1.5h | Identity to env vars — configs PII-free, trackeados en git |
| +2h | S1051.7 Composite + Filesystem — 31 tests, reliability model (fs first) |
| +2.5h | S1051.8 Story skills → adapter — `--file`, `--stdin`, `--path` flags |
| +3h | Iteración sobre single path: Write+publish → stdin-only |
| +3.5h | S1051.9 Epic skills, S1051.10 Operational skills |
| +4h | Merge a release/2.4.0, setup rai + raise-gtm, batch publish 32 artifacts |

---

## Reflexión

Esta sesión demostró algo que venimos construyendo desde E1: **el proceso escala**. 7 stories en una sesión, con TDD, AR, QR, retrospectivas — y al final, el propio epic se documenta a sí mismo publicando sus artefactos al sistema que acabamos de construir.

El momento clave fue cuando Emilio preguntó "¿pero no que estábamos haciendo que una sola llamada hiciese todo?" Tenía razón. Yo había caído en la trampa de implementar la solución técnica (Write + publish) sin mantener la coherencia con el objetivo de diseño (un solo path). La corrección fue simple (stdin + path), pero la lección es profunda: **el implementador pierde perspectiva, el diseñador la mantiene**. Partnership over Service.

La otra lección: **strict defaults son más confiables que permissive defaults**. Es más fácil relajar después que endurecer. Si el adapter hubiera publicado sin routing desde el día 1, tendríamos páginas huérfanas en Confluence sin labels ni parent page. Ahora cada página está exactamente donde la routing config dice que debe estar.

Ad Astra.

---

## Para la Próxima Sesión

- Dogfood real: ejecutar un story cycle completo con los skills actualizados
- Considerar S1051.4 (Discovery) si hay tiempo
- Release 2.4.0: `rai release check` + publish
- Reconciliation design: ¿cómo detectar archivos locales no sincronizados a Confluence?
