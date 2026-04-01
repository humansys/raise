---
epic_id: "RAISE-1162"
grounded_in: "Gemba of Claude Code source tree (~/Code/claude-code-leak-main/claude-code-main/src/)"
---

# Epic Design: Claude Code Architecture Reconstruction

## Source Under Analysis (Gemba)

| Module | Files | Size | RaiSE Relevance |
|--------|------:|-----:|-----------------|
| components/ | 389 | 11M | Baja — UI rendering Ink/React |
| utils/ | 564 | 7.8M | Media — utilidades compartidas, patrones |
| commands/ | 207 | 3.3M | Alta — slash commands, extensión |
| tools/ | 184 | 3.2M | Alta — tool system, permisos |
| services/ | 130 | 2.2M | Alta — MCP, API, compact, analytics |
| hooks/ | 104 | 1.5M | Alta — permission model, tool hooks |
| ink/ | 96 | 1.3M | Baja — rendering framework |
| screens/ | 3 | 1.0M | Baja — REPL, Doctor, Resume |
| bridge/ | 31 | 536K | Media — IDE integration |
| cli/ | 19 | 536K | Media — CLI parsing, print |
| tasks/ | 12 | 368K | Alta — task management |
| skills/ | 20 | 208K | Alta — skill system |
| entrypoints/ | 8 | 176K | Media — SDK, init |
| types/ | 11 | 172K | Media — type definitions |
| keybindings/ | 14 | 172K | Baja — keyboard config |
| constants/ | 21 | 164K | Media — config, feature flags |
| native-ts/ | 4 | 148K | Baja — yoga layout |
| context/ | 9 | 128K | Alta — system/user context |
| memdir/ | 8 | 100K | Alta — persistent memory |
| state/ | 6 | 76K | Alta — state management |
| coordinator/ | 1 | 24K | Alta — multi-agent |
| plugins/ | 2 | 20K | Media — plugin system |
| remote/ | 4 | 48K | Baja — remote sessions |
| query/ | 4 | 36K | Alta — query pipeline |
| **Root files** | | | |
| main.tsx | 1 | 804K | Alta — entrypoint, boot |
| QueryEngine.ts | 1 | 47K | Alta — core LLM caller |
| query.ts | 1 | 69K | Alta — query orchestration |
| Tool.ts | 1 | 30K | Alta — tool base types |
| tools.ts | 1 | 17K | Alta — tool registry |
| commands.ts | 1 | 25K | Alta — command registry |
| interactiveHelpers.tsx | 1 | 57K | Media — interactive UI |
| context.ts | 1 | 6K | Alta — context collection |

## Reconstruction Method (per ADR-016)

### Reconnaissance (S1132.1)

Técnicas a aplicar:
1. **Structural scan** — tree + sizes + file counts (done en pre-design)
2. **Import graph** — extraer imports entre módulos, visualizar clusters
3. **Entry point trace** — main.tsx → setup → query loop → tool dispatch
4. **Public surface** — exports de cada módulo, tipos compartidos
5. **Signal scan** — TODOs, HACKs, feature flags, dead code markers

Salida: `reconnaissance.md` con Module Catalog + Dependency Map + Interest Areas

### Deep Dive Protocol (S1132.2–S1132.6)

Por cada wave:
1. Leer interest areas identificadas en reconnaissance
2. Formular hipótesis: "¿Cómo implementa CC esto? ¿Qué significa para RaiSE?"
3. Leer código fuente relevante (targeted, no exhaustivo)
4. Documentar hallazgo con formato estándar:

```markdown
### Finding F{N}: {título}

**Question:** {pregunta original}
**Files:** {archivos clave analizados}
**Finding:** {lo que encontramos}
**RaiSE Impact:** {implicación accionable}
**Confidence:** {Alta|Media|Baja}
```

### Wave Prioritization

| Wave | Domain | RaiSE Impact | Rationale |
|------|--------|-------------|-----------|
| 1 | Extension Points | Directo | Skills, hooks, tools — literalmente cómo construimos sobre CC |
| 2 | Agent Infrastructure | Directo | Coordinator, tasks, query — informa E3 scaleup-agent |
| 3 | Integration Layer | Directo | MCP, bridge, plugins — informa adapters E1130/E1131 |
| 4 | State & Persistence | Directo | Memory, compact, state — explica bugs que sufrimos |
| 5 | UI & Rendering | Indirecto | Components, Ink — entender pero menor prioridad |

### Synthesis (S1132.7)

- Hallazgos → Jira stories/improvements (estimados, priorizados)
- Patrones → candidatos para adopción en RaiSE (con ADR si significativo)
- Proceso → playbook refinado, lecciones para rai-discover
- Publicación → Confluence, artículos clave

## Key Questions (Hypothesis Seeds)

Preguntas iniciales que la reconnaissance refinará:

1. **Skill lifecycle:** ¿Cómo carga, valida y ejecuta CC un skill? ¿Qué contratos asume?
2. **Hook dispatch:** ¿Cómo se resuelven permisos? ¿Qué información tiene el hook al ejecutarse?
3. **Tool registration:** ¿Cómo se registra un tool? ¿Es extensible o hardcoded?
4. **Agent spawning:** ¿Cómo coordina CC subagentes? ¿Qué contexto comparten?
5. **MCP client:** ¿Cómo gestiona CC conexiones MCP? ¿Qué asume del servidor?
6. **Context window:** ¿Cómo decide CC qué compactar? ¿Qué se pierde?
7. **Memory persistence:** ¿Cómo funciona memdir? ¿Qué triggers activan auto-memory?
8. **Task management:** ¿Cómo persiste y coordina tasks entre agentes?
9. **Plugin system:** ¿Qué puede un plugin? ¿Cuál es el API surface?
10. **Boot sequence:** ¿Qué pasa entre `main.tsx` y el primer prompt? ¿Qué se prefetcha?
