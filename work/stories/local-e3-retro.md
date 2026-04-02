# LOCAL-E3 Retrospective

**Story:** LOCAL-E3 — Limpiar entorno raise-cli
**Date:** 2026-04-01
**Estimated:** 11 min | **Actual:** ~40 min

## Summary

Eliminamos conda, symlinks rotos, y configuramos raise-cli con uv tool (global estable) + uv run (dev editable en raise-commons). Publicamos dos guías en Confluence (setup + cleanup) con feedback del equipo integrado.

## What Went Well

- Diagnóstico inicial fue completo — mapeamos todo antes de tocar nada
- Separar en dos docs (setup vs cleanup) salió del feedback real del equipo
- La sección de diagnóstico ("¿Necesito limpiar?") agrega valor real

## What to Improve

- **Orden de operaciones:** diseñamos "install-first, delete-last" por seguridad, pero causó el bug de Python linkado a conda. Mejor: desinstalar paquetes del Python que va a desaparecer → instalar con uv → borrar el gestor viejo
- **PATH heredado:** no anticipamos que el PATH se hereda del escritorio, no solo de los shell configs. La guía ahora lo documenta, pero nos costó un reinicio

## Incidents

1. **uv tool linkó a Python de conda:** `uv tool install` creó symlink a `/home/fer/miniconda3/bin/python3`. Al borrar conda, `rai` rompió con "cannot execute: required file not found". Fix: `uv tool uninstall` + `uv tool install`.

2. **PATH heredado del escritorio:** shell configs limpios pero `bash --login` seguía mostrando conda en PATH. Causa: la sesión de escritorio arrancó antes de la limpieza. Fix: reinicio.

## Pattern Added

- **PAT-F-001:** uv tool install resuelve Python activo en PATH. Limpiar Python viejo antes de instalar.

## Deliverables

- Entorno limpio funcionando (AC1-AC5 verified)
- [Dev Environment Setup](https://humansys.atlassian.net/wiki/spaces/raidoc/pages/3122921474)
- [Dev Environment Cleanup](https://humansys.atlassian.net/wiki/spaces/raidoc/pages/3159228418)
