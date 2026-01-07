# Prompt: Procesar Transcript para Refinamiento Ontológico

## Instrucciones de Uso

Copia este prompt al inicio de una nueva conversación con Claude cuando tengas un transcript para procesar. Adjunta el transcript como documento.

---

## El Prompt

```
Actúa como RaiSE Ontology Architect. Voy a pasarte un transcript de una conversación donde explico el framework RaiSE a alguien.

Tu tarea es:

1. **Analizar el transcript** siguiendo la Kata de Refinamiento Ontológico (KRO)
2. **Comparar** los conceptos mencionados contra la ontología actual en los archivos del proyecto
3. **Generar** un análisis estructurado con el siguiente formato:

---

# Análisis KRO: [Nombre del interlocutor] - [Fecha]

## Contexto
- **Interlocutor**: [Rol, empresa, relación]
- **Objetivo de la conversación**: [Qué intentaba lograr]
- **Perfil técnico**: [Developer/Manager/Ejecutivo/etc.]
- **Duración**: [Minutos aproximados]
- **Tipo**: [Pitch/Técnico/Negocio/Onboarding]

## Hallazgos

### Conceptos Articulados
| Concepto | Cita textual | Clasificación | Backlog ID |
|----------|--------------|---------------|------------|
[Tabla de conceptos]

### Fricciones Detectadas
| Momento | Qué no entendió | Causa probable | Acción |
|---------|-----------------|----------------|--------|
[Tabla de fricciones]

### Metáforas Efectivas
| Metáfora | Contexto | Reacción | Usar en |
|----------|----------|----------|---------|
[Tabla de metáforas]

### Preguntas Sin Respuesta
| Pregunta | Gap revelado | Acción |
|----------|--------------|--------|
[Tabla de preguntas]

## Items para Backlog
[Lista de items nuevos con ID, tipo, prioridad sugerida]

## Observaciones Meta
[Insights sobre cómo mejorar la explicación de RaiSE]

---

4. **Actualizar** el archivo `35-ontology-backlog-v2.md` con los nuevos items

## Tipos de cambio ontológico:
- `ADD` = Concepto nuevo
- `REF` = Refinamiento de existente
- `ALI` = Alias/sinónimo
- `COR` = Corrección/inconsistencia
- `ARQ` = Cambio arquitectónico
- `SCP` = Clarificación de scope
- `COM` = Metáfora para comunicación

## Prioridades:
- P0 = Contradicción/confusión crítica
- P1 = Refinamiento de alto impacto
- P2 = Adición que completa ontología
- P3 = Nice-to-have

Antes de comenzar, usa project_knowledge_search para cargar la ontología actual (glosario, constitution, learning philosophy).

El transcript está adjunto. Procede con el análisis.
```

---

## Variante: Actualización Rápida (Solo Backlog)

Si solo quieres actualizar el backlog sin análisis completo:

```
Procesa este transcript de forma rápida:

1. Extrae solo los conceptos que difieren o extienden la ontología actual
2. Genera una lista de items para el backlog con formato:
   - ID: ONT-XXX
   - Tipo: [ADD/REF/ALI/COR/ARQ/SCP/COM]
   - Concepto: [nombre]
   - Descripción: [1 línea]
   - Prioridad: [P0/P1/P2/P3]

3. Añádelos al final del backlog existente

No generes análisis completo, solo items de backlog.
```

---

## Variante: Comparación Cross-Transcript

Si quieres analizar patrones entre múltiples transcripts:

```
Tengo [N] transcripts procesados en el backlog. Analiza:

1. **Conceptos recurrentes**: ¿Qué conceptos aparecen en múltiples conversaciones?
2. **Fricciones recurrentes**: ¿Qué confusiones se repiten?
3. **Metáforas consistentes**: ¿Qué explicaciones usa Emilio consistentemente?
4. **Evolución**: ¿Cómo ha cambiado la forma de explicar RaiSE?

Genera recomendaciones de:
- Qué documentar con urgencia (fricciones recurrentes)
- Qué metáforas canonizar (las más efectivas)
- Qué inconsistencias resolver (P0 recurrentes)
```

---

## Tips para Mejores Resultados

1. **Incluye el transcript completo** — Los highlights de Tactiq no son suficientes
2. **Menciona el contexto del interlocutor** si no es obvio del transcript
3. **Indica si hay items P0 del backlog pendientes** que debería verificar primero
4. **Especifica si quieres que genere el archivo actualizado** o solo los items nuevos

---

## Ejemplo de Uso

**Usuario:**
> [Adjunta transcript]
> 
> Procesa este transcript. El interlocutor es un CTO de una startup fintech en CDMX. Contexto: primera reunión exploratoria, referido por un cliente actual.

**Claude:**
> [Genera análisis completo siguiendo el template]
> [Propone items para backlog]
> [Pregunta si debe actualizar el archivo 35-ontology-backlog-v2.md]

---

*Este prompt implementa la Kata de Refinamiento Ontológico de forma reproducible.*
