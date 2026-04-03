# SOP: Snyk Dependency Monitoring

> Standard Operating Procedure for scanning and uploading dependency snapshots to Snyk cloud
> Version: 2.0
> Date: 2026-03-31
> Status: Active

---

## Purpose

Mantener visibilidad continua de vulnerabilidades en dependencias del proyecto mediante Snyk cloud. El monitoreo notifica automáticamente cuando aparecen nuevas CVEs en las dependencias instaladas.

**Alcance:** Un proyecto rastreado en Snyk org `aquileslazaroh`:
- `raise-commons` — Python (root `/`)

> **Nota:** El proyecto `raise-docs` (frontend Node.js en `site/`) fue eliminado en RAISE-1129.
> La documentación ahora usa MkDocs (Python) — sus dependencias están incluidas en el scan Python.

---

## Prerequisitos

- `snyk` CLI instalado y autenticado (`snyk auth`)
- Org: `aquileslazaroh`

---

## Python (`raise-commons`)

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

## Cuándo ejecutar

| Evento | Acción |
|--------|--------|
| Merge a release branch | `snyk monitor` Python |
| Dependabot alert recibido | `snyk test` local → fix → `snyk monitor` |
| Release a `main` | `snyk monitor` Python |

---

## Límite de plan

Snyk org `aquileslazaroh` tiene límite de 200 tests privados/mes. `snyk monitor` consume 1 test por ejecución. Priorizar `snyk test` local para diagnóstico; reservar `snyk monitor` para post-fix y post-merge.
