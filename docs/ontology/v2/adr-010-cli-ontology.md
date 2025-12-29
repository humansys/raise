# ADR-010: Ontología de Comandos CLI

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-29  
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

El diseño inicial de comandos CLI incluía terminología inconsistente y confusa:

| Comando Original | Problema |
|------------------|----------|
| `raise hydrate` | Jerga de frontend (React), no autoexplicativo |
| `raise validate` | Confuso: las Katas no se "validan", se ejecutan |
| `raise check` vs `validate` | Ambigüedad entre ambos comandos |

Adicionalmente, no había distinción clara entre comandos para **desarrollo interactivo** (requieren Orquestador) y comandos para **CI/CD** (automatizables).

### Principio de Jidoka como Guía

El principio Jidoka (自働化) establece que la automatización debe incluir "toque humano" cuando se detectan anomalías. Esto define una frontera natural:

- **Procesos con Escalation posible** → Requieren humano presente → Solo desarrollo
- **Verificaciones binarias (pass/fail)** → Automatizables → CI/CD compatible

---

## Decisión

### 1. Renombrar Comandos

| Antes | Después | Razón |
|-------|---------|-------|
| `raise hydrate` | `raise pull` | Verbo familiar (Git), acción clara |
| `raise validate` | `raise kata` | Kata es proceso que se ejecuta, no se valida |

### 2. Clasificar Comandos por Contexto

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMANDOS CLI v0.1                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DESARROLLO (Interactivo)          CI/CD (Automatizable)        │
│  ─────────────────────────         ─────────────────────        │
│  raise init                        raise pull                   │
│  raise kata <alias>                raise check [path]           │
│                                    raise gate <gate-id>         │
│                                    raise audit [options]        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Estructura Final de Comandos MVP

| Comando | Contexto | Interactivo | Exit Code | Descripción |
|---------|----------|:-----------:|:---------:|-------------|
| `raise init` | Dev | ✅ | — | Inicializar proyecto |
| `raise pull` | Ambos | ❌ | 0/1 | Sincronizar Golden Data |
| `raise kata <alias>` | Dev | ✅ | — | Ejecutar proceso Jidoka |
| `raise check [path]` | Ambos | ❌ | 0/1 | Verificar guardrails |
| `raise gate <id>` | Ambos | ❌ | 0/1 | Verificar Validation Gate |
| `raise audit` | Ambos | ❌ | 0 | Exportar Observable Workflow |

### 4. Aliases de Kata

```bash
raise kata spec         # → L1-spec-writing
raise kata plan         # → L1-implementation-plan
raise kata design       # → L1-technical-design
raise kata review       # → L2-code-review
raise kata L2-03        # → Por ID explícito
```

### 5. Flags Actualizados

| Flag Antes | Flag Después |
|------------|--------------|
| `--skip-hydrate` | `--skip-pull` |
| `--guardrails-only` | (mantener) |

---

## Consecuencias

### Positivas

- **Claridad semántica:** `pull` es universalmente entendido
- **Coherencia ontológica:** `kata` refleja que es proceso, no validación
- **Distinción clara:** Desarrollo vs CI/CD bien definidos
- **KISS:** Comandos mínimos para MVP
- **Jidoka explícito:** Solo `kata` puede escalar a humano

### Negativas

- **Migración:** Documentación existente debe actualizarse
- **Breaking change:** Usuarios de `hydrate` deben migrar

### Neutras

- Aliases legacy pueden mantenerse durante v0.x (`hydrate` → `pull`)

---

## Principio de Diseño Emergente

> **"Los comandos de VERIFICACIÓN son automatizables (CI/CD). Los comandos de CREACIÓN requieren humano (Dev)."**

| Tipo | Comandos | Característica |
|------|----------|----------------|
| **Creación** | `init`, `kata` | Requieren juicio humano, pueden escalar |
| **Verificación** | `pull`, `check`, `gate`, `audit` | Determinísticos, exit codes |

---

## Flujo de Uso

### Desarrollo (Terminal del Orquestador)

```bash
$ raise pull                     # Traer Golden Data fresco
$ raise kata spec FEAT-123       # Proceso interactivo con Jidoka
  ├── [1/3] Gathering context    ✓
  ├── [2/3] Defining scope       ⚠ Escalation
  │   └── Orquestador decide...
  └── [3/3] Writing spec         ✓

$ raise check src/               # Verificar guardrails
$ raise gate Gate-Design         # ¿Puedo avanzar?
```

### CI/CD (GitHub Actions)

```yaml
steps:
  - run: raise pull              # Sincronizar
  - run: raise check --strict    # Verificar (exit 0/1)
  - run: raise gate Gate-Code    # Gate (exit 0/1)
  - run: raise audit --format json
```

---

## Comandos Diferidos (YAGNI)

Los siguientes comandos se excluyen del MVP por YAGNI:

| Comando | Razón de exclusión | Versión target |
|---------|-------------------|----------------|
| `raise generate` | Puede ser parte de `kata` | v0.2 |
| `raise mcp` | Puede ser automático en `init` | v0.2 |
| `raise guardrail` | Mayoría usa `pull` + `check` | v0.2 |

---

## Migración

### Aliases Temporales (v0.x)

```python
# En CLI, mantener aliases para backwards compatibility
@cli.command()
@click.pass_context
def hydrate(ctx):
    """[DEPRECATED] Use 'raise pull' instead."""
    click.echo("Warning: 'hydrate' is deprecated. Use 'raise pull'.")
    ctx.invoke(pull)
```

### Documentación

Ver sección "Impacto en Documentos" para lista de archivos a actualizar.

---

## Referencias

- [21-methodology-v2.md](../21-methodology-v2.md) — Flujo de valor
- [05-learning-philosophy-v2.md](../05-learning-philosophy-v2.md) — Principio de Jidoka
- Toyota Production System — Jidoka (自働化)

---

*Este ADR establece la ontología de comandos CLI para RaiSE v0.1 MVP.*
