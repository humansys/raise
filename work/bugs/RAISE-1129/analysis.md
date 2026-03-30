# RAISE-1129: Analysis

## 5 Whys

1. **¿Por qué está caído docs.raiseframework.com?** → No hay deploy reciente del contenido de docs/
2. **¿Por qué no hay deploy?** → deploy-site.yml despliega site/ al proyecto raise-gtm, no docs/
3. **¿Por qué apunta a site/?** → Se creó cuando marketing y docs vivían juntos; al separar, no se actualizó
4. **¿Por qué no se actualizó?** → RAISE-532 documentó la decisión pero el pipeline de docs quedó pendiente
5. **Root cause:** Separación de repos sin crear pipeline de deploy para documentación

## Root Cause

Al separar raise-commons (código + docs) de raise-gtm (marketing), el workflow
`deploy-site.yml` quedó configurado para el sitio marketing (`site/` → proyecto
`raise-gtm`). Nunca se creó un workflow equivalente para desplegar `docs/` a
Cloudflare Pages con su propio proyecto.

## Fix Approach

**Opción elegida:** Crear `deploy-docs.yml` que construya y despliegue `docs/` a
un proyecto Cloudflare Pages dedicado (e.g., `raise-docs`).

Dado que la migración a MkDocs (RAISE-823) reemplazará Astro pronto, el fix
es mínimo: un workflow funcional que despliegue el Astro existente de `docs/`.

**No hacer ahora:**
- No migrar a MkDocs (eso es RAISE-823)
- No tocar el workflow de raise-gtm (ese funciona)
