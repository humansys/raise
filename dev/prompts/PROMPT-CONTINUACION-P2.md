# Prompt de Continuación: Migración ADR-010 — Documentos P2

## Contexto

En la sesión del 2025-12-29 se completó la migración de ontología de comandos CLI (ADR-010):

| Cambio | Antes | Después |
|--------|-------|---------|
| Comando de sincronización | `rai hydrate` | `rai pull` |
| Comando de ejecución de katas | `rai validate` | `rai kata` |
| Flag | `--skip-hydrate` | `--skip-pull` |

**ADR-010** documenta la decisión y clasifica comandos en dos contextos:
- **Desarrollo (interactivo):** `rai init`, `rai kata`
- **CI/CD (automatizable):** `rai pull`, `rai check`, `rai gate`, `rai audit`

---

## Progreso Actual

| Prioridad | Documentos | Estado |
|-----------|------------|--------|
| 🔴 P0 | 23-commands-reference, 10-system-architecture | 1/2 ✅ |
| 🟡 P1 | 30-roadmap, 11-data-arch, 24-examples, 15-tech-stack | 4/4 ✅ |
| 🟢 P2 | 01-vision, 12-integration, 13-security, 20-glossary | 0/4 ⬜ |

---

## Tarea: Actualizar Documentos P2

### Documentos Pendientes

| Documento | Menciones | Cambio Requerido |
|-----------|-----------|------------------|
| `10-system-architecture-v2.md` | 5 hydrate, 1 validate | Diagramas Mermaid + texto |
| `01-product-vision-v2.md` | 2 hydrate | Buscar/reemplazar |
| `12-integration-patterns-v2.md` | 1 validate | Buscar/reemplazar |
| `13-security-compliance-v2.md` | 1 hydrate | Buscar/reemplazar |
| `20-glossary-v2.md` | 1 hydrate | Añadir términos nuevos |

### Patrones de Reemplazo

```bash
# Reemplazos globales
sed -i 's/raise hydrate/raise pull/g' <archivo>
sed -i 's/raise validate/raise kata/g' <archivo>
sed -i 's/--skip-hydrate/--skip-pull/g' <archivo>
sed -i 's/hydrate\.py/pull.py/g' <archivo>

# Actualizar versión
sed -i 's/2\.0\.0/2.1.0/g' <archivo>
```

### Cambios Especiales

**20-glossary-v2.md** — Añadir entradas:

```markdown
### pull (comando)
**Definición:** Comando CLI que sincroniza Golden Data desde el repositorio central (raise-config).
**Uso:** `rai pull [--branch <nombre>] [--guardrails-only]`
**Contexto:** Desarrollo + CI/CD
**Nota:** Reemplaza `hydrate` desde v2.1 (ADR-010).

### kata (comando)
**Definición:** Comando CLI que ejecuta una Kata (proceso estructurado con Jidoka).
**Uso:** `rai kata <alias|id> [target]`
**Contexto:** Solo desarrollo (interactivo)
**Aliases:** spec, plan, design, review, story
**Nota:** Reemplaza `validate` desde v2.1 (ADR-010). Las Katas se ejecutan, no se validan.
```

**10-system-architecture-v2.md** — Diagramas Mermaid a actualizar:
- Flujo 2: "Sincronización de Guardrails" menciona `rai hydrate`
- Tabla de comandos raise-kit
- Secuencia de inicialización

---

## Verificación Post-Actualización

```bash
# Verificar que no queden menciones legacy
cd /mnt/project
grep -r "raise hydrate" *.md
grep -r "raise validate" *.md  # Solo debe aparecer como concepto, no comando
grep -r "skip-hydrate" *.md

# Debe retornar 0 resultados
```

---

## Archivos de Referencia

Los siguientes archivos ya fueron actualizados y pueden usarse como referencia:

- `23-commands-reference-v2.1.md` — Referencia canónica de comandos
- `adr-010-cli-ontology.md` — Decisión arquitectónica
- `adr-010-impact-analysis.md` — Tracking de migración

---

## Instrucción

Por favor continúa con la actualización de los documentos P2 listados arriba. Para cada documento:

1. Copiar a `/home/claude/`
2. Aplicar reemplazos con sed
3. Actualizar versión a 2.1.0
4. Verificar que no queden menciones legacy
5. Copiar a `/mnt/user-data/outputs/`

Para `20-glossary-v2.md`, además añade las nuevas entradas de `pull` y `kata` como comandos.

Al finalizar, actualiza `adr-010-impact-analysis.md` con el progreso y genera un resumen de cambios.
