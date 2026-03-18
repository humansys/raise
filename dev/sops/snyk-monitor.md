# SOP: Snyk Dependency Monitoring

> Standard Operating Procedure for scanning and uploading dependency snapshots to Snyk cloud
> Version: 1.0
> Date: 2026-03-18
> Status: Active

---

## Purpose

Mantener visibilidad continua de vulnerabilidades en dependencias del proyecto mediante Snyk cloud. El monitoreo notifica automáticamente cuando aparecen nuevas CVEs en las dependencias instaladas.

**Alcance:** Dos proyectos rastreados en Snyk org `aquileslazaroh`:
- `raise-commons` — backend Python (root `/`)
- `raise-docs` — frontend Node.js (`site/`)

---

## Prerequisitos

- `snyk` CLI instalado y autenticado (`snyk auth`)
- Org: `aquileslazaroh`

---

## Python Backend (`raise-commons`)

### Problema
`snyk monitor --all-projects` ignora `uv.lock`. Snyk requiere `pip` y un `requirements.txt` explícito.

### Pasos

```bash
# 1. Instalar pip en el venv (uv no lo incluye por defecto)
uv pip install pip

# 2. Generar requirements.txt desde el venv (NO desde conda/sistema)
.venv/bin/pip freeze | grep -v '^-e' > /tmp/req.txt

# 3. Subir snapshot a Snyk cloud
snyk monitor \
  --file=/tmp/req.txt \
  --command=.venv/bin/python \
  --package-manager=pip \
  --org=aquileslazaroh \
  --project-name=raise-commons
```

### Verificación local (sin subir)

```bash
snyk test \
  --file=/tmp/req.txt \
  --command=.venv/bin/python \
  --package-manager=pip \
  --org=aquileslazaroh
```

### Notas
- Usar `.venv/bin/pip freeze`, no `pip freeze` — el pip del sistema/conda incluye paquetes ajenos al proyecto
- `uv export` puede fallar si hay workspace members sin `pyproject.toml`; usar `pip freeze` es más robusto

---

## Frontend (`raise-docs`)

### Ubicación
El frontend está en `site/` (no `docs/`).

### Prerequisito
`node_modules` debe existir. Si no:

```bash
cd site && npm install
```

### Pasos

```bash
cd site

snyk monitor \
  --file=package.json \
  --org=aquileslazaroh \
  --project-name=raise-docs
```

### Verificación local (sin subir)

```bash
cd site && snyk test --file=package.json --org=aquileslazaroh
```

---

## Dependencias transitivas vulnerables

Cuando Snyk reporta vulnerabilidades en dependencias transitivas de Node.js, la solución es agregar `overrides` en `site/package.json`:

```json
"overrides": {
  "nombre-paquete": ">=version-parcheada"
}
```

Luego `npm install` para aplicar. Verificar con `npm list nombre-paquete`.

---

## Cuándo ejecutar

| Evento | Acción |
|--------|--------|
| Merge a `dev` | `snyk monitor` Python + Node |
| Dependabot alert recibido | `snyk test` local → fix → `snyk monitor` |
| Release a `main` | `snyk monitor` Python + Node |

---

## Límite de plan

Snyk org `aquileslazaroh` tiene límite de 200 tests privados/mes. `snyk monitor` consume 1 test por ejecución. Priorizar `snyk test` local para diagnóstico; reservar `snyk monitor` para post-fix y post-merge.
