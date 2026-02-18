---
id: "ADR-031"
title: "IDE Abstraction Layer — IdeConfig Pattern"
date: "2026-02-17"
status: "Accepted"
---

# ADR-031: IDE Abstraction Layer — IdeConfig Pattern

## Contexto

`rai init` tiene 6 puntos hardcoded a Claude Code: paths de skills (`.claude/skills/`), archivo de instrucciones (`CLAUDE.md`), memory path (`~/.claude/projects/`), y el locator/builder que consumen esos paths. Para soportar Antigravity (y futuros IDEs) necesitamos desacoplar sin over-engineering.

## Decisión

Introducir `IdeType` (Literal) e `IdeConfig` (dataclass) con factory function. Cada IDE se define como un `IdeConfig` con sus paths. El IDE elegido se persiste en `manifest.yaml` bajo `ide.type`. `claude` es el default.

```python
IdeConfig(
    skills_dir=".agent/skills",
    instructions_file=".agent/rules/raise.md",
    memory_path=None,  # Antigravity no tiene equivalente
    workflows_dir=".agent/workflows",
)
```

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Agregar un IDE nuevo = agregar un `IdeConfig`, no tocar lógica |
| ✅ Positivo | Backward compatible — `claude` es default, sin flag = sin cambio |
| ✅ Positivo | Manifest persiste la elección — CLI sabe qué IDE usa el proyecto |
| ⚠️ Negativo | Cada función que usa paths de skills necesita refactor (6 archivos) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| If/else por IDE en cada función | No escala, duplica lógica |
| Registry/adapter con ABC | Over-engineering para 2 IDEs |
| Path configurable en pyproject.toml | Mezcla config de build con config de IDE |

---

<details>
<summary><strong>Referencias</strong></summary>

- SES-006: Investigación de portabilidad multi-IDE
- `dev/rai-architecture-discovery.md` §7-8
- RAISE-128: IDE Integration epic

</details>
