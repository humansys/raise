# Prompt: Continuar Fase A1 - Crear JSON Schemas para RaiSE

## Contexto

Estamos desarrollando **RaiSE Framework v2.1** (Reliable AI Software Engineering), un framework de gobernanza para desarrollo AI-assisted. Hoy completamos la formalización de la arquitectura v2.1 con 7 categorías de comandos.

**Estado actual**: Track A (Open Core), Fase A1 - Foundation & Schemas

## Documentos de Referencia

Lee estos documentos para entender el contexto completo:

1. **Vision general**: `/specs/raise/vision.md` - Framework completo v2.1
2. **Diseño técnico**: `/specs/raise/design.md` - Contratos de datos (sección 3)
3. **Roadmap**: `/specs/raise/roadmap.md` - Tareas A1.1 a A1.4
4. **ADRs relevantes**:
   - `/specs/raise/adrs/adr-003-yaml-rule-format.md` - YAML para reglas
   - `/specs/raise/adrs/adr-004-separate-graph.md` - Grafo separado

## Tarea

Crear los JSON Schemas que definen el contrato de datos entre los componentes SAR (extracción) y CTX (entrega de contexto).

### Entregables

1. **`rule-schema.json`** - Schema para regla unitaria
   - Ubicación: `/specs/raise/schemas/rule-schema.json`
   - Campos requeridos: id, version, status, category, confidence, enforcement, title, intent, pattern, examples, provenance
   - Ver estructura lean en `design.md` sección 3.1

2. **`graph-schema.json`** - Schema para grafo de relaciones
   - Ubicación: `/specs/raise/schemas/graph-schema.json`
   - Campos: version, generated_date, nodes, edges
   - Tipos de edges: requires, conflicts_with, supersedes, related_to
   - Ver estructura en `design.md` sección 3.2

3. **`mvc-schema.json`** - Schema para output de CTX (MVC)
   - Ubicación: `/specs/raise/schemas/mvc-schema.json`
   - Campos: query, primary_rules, context_rules, warnings, graph_context, metadata
   - Ver estructura en `design.md` sección 3.3

4. **Ejemplos de validación** - Al menos 2 ejemplos por schema
   - Ubicación: `/specs/raise/schemas/examples/`
   - Ejemplos realistas basados en convenciones TypeScript

### Criterios de Aceptación

- [ ] Schemas son JSON Schema Draft 2020-12 válidos
- [ ] Cada schema tiene descripción en cada campo
- [ ] Ejemplos pasan validación contra su schema
- [ ] Schemas cubren todos los campos documentados en `design.md`
- [ ] Incluir README.md explicando uso de los schemas

### Principios a Seguir

1. **Lean**: Solo campos necesarios, evitar over-engineering
2. **Explícito**: Cada campo debe tener `description`
3. **Validable**: Usar `enum` para valores fijos, `pattern` para formatos
4. **Extensible**: Usar `additionalProperties: false` pero permitir evolución via versioning

## Estructura Esperada

```
specs/raise/schemas/
├── README.md                    # Guía de uso
├── rule-schema.json             # Schema de regla unitaria
├── graph-schema.json            # Schema de grafo
├── mvc-schema.json              # Schema de output CTX
└── examples/
    ├── rule-example-naming.yaml
    ├── rule-example-architecture.yaml
    ├── graph-example.yaml
    └── mvc-example.yaml
```

## Comando para Empezar

```
Por favor lee los documentos de referencia mencionados arriba y luego crea los JSON Schemas siguiendo las especificaciones. Empieza con rule-schema.json ya que es el más importante.
```
