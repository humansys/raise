# rai-server — Forge Demo Handoff

Documento para el desarrollador que construirá el Rovo Agent en Atlassian Forge.
Cubre todo: levantar el server, la BD, los endpoints reales, los mocks necesarios, y cómo simular el ingest de Confluence a mano.

---

## 1. Levantar el server local

### Prerequisitos

- Docker (tu usuario debe estar en el grupo `docker`)
- uv
- Python 3.12+

Si Docker da `permission denied`:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Pasos (desde la raíz del repo `raise-commons/`)

```bash
# 1. Levantar postgres + server
docker compose up --build

# 2. Migraciones (primera vez o después de docker compose down -v)
cd packages/rai-server
RAI_DATABASE_URL=postgresql+asyncpg://rai:rai_dev@localhost:5432/rai uv run alembic upgrade head

# 3. Seed de datos dev (org + API key)
cd ../..
docker compose exec -T postgres psql -U rai -d rai < packages/rai-server/scripts/seed_dev.sql

# 4. Verificar
curl http://localhost:8000/health
# → {"status":"ok","database":"connected","version":"0.1.0"}
```

Server corriendo en `http://localhost:8000`.

---

## 2. La base de datos

Postgres corre en el contenedor Docker. Los datos persisten en un volumen llamado `pgdata`.
Para reiniciar desde cero: `docker compose down -v` y repetir los pasos de setup.

### Tablas relevantes para el demo

```
organizations        → el tenant (org "RaiSE Dev")
  └── api_keys       → autenticación (key: rsk_dev_test_key_12345)
  └── graph_nodes    → nodos del knowledge graph (módulos, decisiones, patrones)
  └── graph_edges    → relaciones entre nodos
  └── memory_patterns → patrones aprendidos
  └── agent_events   → telemetría (append-only)
```

Toda la data está bajo `org_id = 00000000-0000-4000-8000-000000000001` (RaiSE Dev).

### Conexión directa a postgres (para debug)

```bash
docker compose exec -T postgres psql -U rai -d rai
```

Desde psql:
```sql
SELECT * FROM organizations;
SELECT * FROM api_keys;
SELECT node_id, node_type, content FROM graph_nodes;
SELECT content FROM memory_patterns;
```

---

## 3. Autenticación

Todos los endpoints (excepto `/health`) requieren:

```
Authorization: Bearer rsk_dev_test_key_12345
```

El server hashea el token con SHA-256 y lo valida contra `api_keys`. Nunca almacena el raw key.

---

## 4. Endpoints existentes (reales, funcionan hoy)

### Health
```bash
GET /health
# Sin auth. Verificar antes de cualquier operación.
curl http://localhost:8000/health
```

### Graph — consultar
```bash
GET /api/v1/graph/query?q=<keyword>&limit=<n>

curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  "http://localhost:8000/api/v1/graph/query?q=auth&limit=5"
```

Respuesta:
```json
{
  "results": [
    {
      "node_id": "mod-auth",
      "node_type": "module",
      "content": "API key authentication module",
      "source_file": "src/rai_server/auth.py",
      "rank": 0.06
    }
  ],
  "total": 1,
  "query": "auth",
  "limit": 5
}
```

### Graph — sync (subir nodos)
```bash
POST /api/v1/graph/sync

curl -X POST \
  -H "Authorization: Bearer rsk_dev_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "raise-commons",
    "nodes": [
      {
        "node_id": "decision-auth-001",
        "node_type": "decision",
        "scope": "project",
        "content": "Usar SHA-256 para hash de API keys — irreversible, sin rainbow tables",
        "source_file": null,
        "properties": {}
      }
    ],
    "edges": []
  }' \
  http://localhost:8000/api/v1/graph/sync
```

### Memory — guardar patrón
```bash
POST /api/v1/memory/patterns

curl -X POST \
  -H "Authorization: Bearer rsk_dev_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "Siempre correr migraciones antes del seed", "context": ["setup"], "properties": {}}' \
  http://localhost:8000/api/v1/memory/patterns
```

### Memory — listar patrones
```bash
GET /api/v1/memory/patterns?limit=50

curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  http://localhost:8000/api/v1/memory/patterns
```

### Agent — registrar evento
```bash
POST /api/v1/agent/events

curl -X POST \
  -H "Authorization: Bearer rsk_dev_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "confluence.page.queried", "payload": {"page_id": "PAGE-123"}}' \
  http://localhost:8000/api/v1/agent/events
```

### Agent — listar eventos
```bash
GET /api/v1/agent/events?limit=20

curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  http://localhost:8000/api/v1/agent/events
```

---

## 5. Endpoints faltantes — mockear en Forge

Estos tres endpoints no existen en rai-server todavía. Se mockean directamente en las Forge actions. Cuando el endpoint real exista, solo se cambia el `return` hardcodeado por un `fetch()`.

### Mock: session-start

```javascript
// Forge action: session-start
// Simula GET /api/v1/context/bundle (no existe aún)
export async function sessionStart() {
  // TODO: reemplazar con:
  // const res = await fetch(`${RAI_SERVER_URL}/api/v1/context/bundle`, {
  //   headers: { Authorization: `Bearer ${RAI_API_KEY}` }
  // })
  // return await res.json()

  return {
    session_id: "SES-050",
    bundle: `
Developer: Fer (shu)
Story: rai-server-docs
Branch: story/standalone/rai-server-docs

Last: SES-049 — Sync de dev, merge de 123 commits

Pending:
- Validar endpoints de rai-server
- Documentar README

Governance:
- Siempre correr migraciones antes del seed
- Validar payload contra código fuente antes de documentar
    `.trim()
  }
}
```

### Mock: context-close

```javascript
// Forge action: context-close
// Simula POST /api/v1/context/close (no existe aún)
export async function contextClose({ summary, narrative, next_prompt, patterns }) {
  // TODO: reemplazar con:
  // const res = await fetch(`${RAI_SERVER_URL}/api/v1/context/close`, {
  //   method: "POST",
  //   headers: {
  //     Authorization: `Bearer ${RAI_API_KEY}`,
  //     "Content-Type": "application/json"
  //   },
  //   body: JSON.stringify({ summary, narrative, next_prompt, patterns })
  // })
  // return await res.json()

  // Los patrones sí se guardan reales en el server
  if (patterns?.length) {
    for (const p of patterns) {
      await fetch(`${RAI_SERVER_URL}/api/v1/memory/patterns`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${RAI_API_KEY}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(p)
      })
    }
  }

  return {
    session_id: "SES-050",
    status: "closed",
    patterns_saved: patterns?.length ?? 0,
    next_prompt_saved: !!next_prompt
  }
}
```

> Nota: `context-close` sí puede guardar los patrones reales via `POST /api/v1/memory/patterns` aunque el endpoint de close no exista. Solo el narrative y next_prompt quedan sin persistir hasta que el endpoint esté listo.

---

## 6. Cómo simular ingest de Confluence a mano

El endpoint `POST /api/v1/ingest` no existe aún. En su lugar, el contenido de Confluence se agrega manualmente al grafo en dos pasos:

### Paso 1 — Agregar el contenido como nodo via graph/sync

Toma el contenido de la página de Confluence y mándalo directamente como nodo:

```bash
curl -X POST \
  -H "Authorization: Bearer rsk_dev_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "raise-commons",
    "nodes": [
      {
        "node_id": "confluence-PAGE-4521",
        "node_type": "document",
        "scope": "project",
        "content": "Decisión de arquitectura: usamos SHA-256 para hashing de API keys. Razones: irreversibilidad, sin rainbow tables, estándar en la industria. El raw key nunca se almacena.",
        "source_file": null,
        "properties": {
          "source": "confluence",
          "page_id": "PAGE-4521",
          "title": "Auth Architecture Decision",
          "url": "https://tu-confluence/pages/4521"
        }
      }
    ],
    "edges": []
  }' \
  http://localhost:8000/api/v1/graph/sync
```

### Paso 2 — Verificar que quedó en el grafo

```bash
curl -H "Authorization: Bearer rsk_dev_test_key_12345" \
  "http://localhost:8000/api/v1/graph/query?q=SHA-256"
```

Debe aparecer el nodo con `node_id: confluence-PAGE-4521`.

### Para el demo

El flujo manual es:
1. Copias el contenido relevante de las páginas de Confluence
2. Lo mandas via `POST /api/v1/graph/sync` con `node_type: "document"` y `properties.source: "confluence"`
3. El Forge agent consulta `GET /api/v1/graph/query` y obtiene esos nodos
4. Para el demo es indistinguible del ingest automático

---

## 7. Exponer el server para Forge (tunnel)

Forge necesita HTTPS para llamar APIs externas. Para desarrollo local:

```bash
# Opción A: ngrok
ngrok http 8000
# → https://abc123.ngrok.io

# Opción B: cloudflared
cloudflared tunnel --url http://localhost:8000
# → https://xyz.trycloudflare.com
```

La URL del tunnel va en el `manifest.yml` de Forge:

```yaml
permissions:
  external:
    fetch:
      client:
        - 'https://abc123.ngrok.io'
```

Y como variable de entorno en las actions:
```javascript
const RAI_SERVER_URL = "https://abc123.ngrok.io"
const RAI_API_KEY = "rsk_dev_test_key_12345"
```

---

## 8. Flujo completo del demo

```
1. Usuario abre Confluence
2. Invoca el Rovo Agent

3. "Inicia sesión"
   → action: session-start (mock)
   → agente carga contexto: story activa, pending, governance

4. "¿Qué sabemos sobre autenticación?"
   → action: query-graph
   → GET /api/v1/graph/query?q=autenticacion
   → agente responde con nodos reales del grafo

5. "Guarda que siempre hay que validar el payload antes de documentar"
   → action: save-pattern
   → POST /api/v1/memory/patterns
   → guardado en postgres real

6. "Registra que revisamos la página de auth"
   → action: log-event
   → POST /api/v1/agent/events { event_type: "confluence.page.reviewed" }

7. "Cierra la sesión"
   → action: context-close (mock)
   → patrones del paso 5 ya están en postgres
   → narrative y next_prompt mockeados como "guardados"
```

Los pasos 4, 5 y 6 son 100% reales contra postgres. Los pasos 3 y 7 son mock en Forge hasta que los endpoints `/context/bundle` y `/context/close` existan.
