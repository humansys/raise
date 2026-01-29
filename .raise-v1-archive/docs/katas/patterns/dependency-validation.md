---
id: patron-04-dependency-validation
nivel: patron
titulo: "Validación Técnica de Dependencias"
audience: intermediate
template_asociado: null
validation_gate: null
prerequisites:
  - principios-00-meta-kata
  - patron-01-code-analysis
tags: [dependencias, validacion, seguridad, patron]
version: 1.0.0
---

# Validación Técnica de Dependencias

## Propósito

Establecer un proceso para evaluar y validar dependencias antes de incorporarlas a un proyecto. Este patrón responde a: **¿Qué forma tiene una evaluación rigurosa de dependencias?**

## Cuándo Aplicar

- Antes de agregar una nueva dependencia
- Durante auditorías de seguridad
- Al actualizar dependencias existentes
- Para evaluar alternativas tecnológicas

---

## Estructura de Validación

### Paso 1: Definir Necesidad

Antes de buscar dependencias, clarificar:
- ¿Qué problema específico resuelve?
- ¿Por qué no resolverlo con código propio?
- ¿Cuál es el costo de NO tener esta dependencia?

**Verificación:** Puedes justificar la necesidad en una oración sin mencionar la dependencia específica.

> **Si no puedes continuar:** Necesidad no clara → La dependencia puede ser innecesaria. Evaluar si el problema se resuelve con lo existente.

---

### Paso 2: Identificar Candidatos

Buscar opciones que resuelvan la necesidad:
- Mínimo 2-3 alternativas
- Incluir la opción "hacer nosotros mismos"
- Considerar lo que ya está en el stack

**Verificación:** Lista de candidatos con pros/cons iniciales de cada uno.

> **Si no puedes continuar:** Solo hay una opción → Ampliar búsqueda. Si realmente solo hay una, documentar el monopolio como riesgo.

---

### Paso 3: Evaluar Salud del Proyecto

Para cada candidato, verificar:
- ¿Mantenimiento activo? (commits recientes, issues respondidos)
- ¿Comunidad saludable? (contribuidores, estrellas, forks)
- ¿Documentación adecuada?
- ¿Versión estable? (>1.0, semver)

**Verificación:** Scorecard de salud para cada candidato.

> **Si no puedes continuar:** Proyecto abandonado pero funcional → Evaluar si se puede fork/mantener internamente. Alto riesgo requiere plan de contingencia.

---

### Paso 4: Auditar Seguridad

Revisar aspectos de seguridad:
- ¿Vulnerabilidades conocidas? (CVEs, Snyk, npm audit)
- ¿Dependencias transitivas problemáticas?
- ¿Historial de respuesta a issues de seguridad?
- ¿Licencia compatible con el proyecto?

**Verificación:** Reporte de seguridad sin vulnerabilidades críticas o con plan de mitigación.

> **Si no puedes continuar:** Vulnerabilidad crítica sin parche → No usar. Buscar alternativa o implementar solución propia para esa funcionalidad.

---

### Paso 5: Evaluar Compatibilidad

Verificar que funciona con el stack actual:
- Versión de lenguaje/runtime compatible
- Sin conflictos con dependencias existentes
- Tamaño de bundle aceptable (si aplica)
- Performance adecuada

**Verificación:** PoC mínimo funcionando en el entorno real del proyecto.

> **Si no puedes continuar:** Conflicto de versiones → Evaluar si se puede resolver con aliases o si requiere actualizar otras dependencias. El costo total puede invalidar la dependencia.

---

### Paso 6: Documentar Decisión

Registrar la elección y su justificación:
- Problema que resuelve
- Alternativas consideradas
- Por qué se eligió esta opción
- Riesgos identificados y mitigaciones
- Plan de actualización

**Verificación:** Documento que permite a alguien futuro entender por qué se tomó esta decisión.

> **Si no puedes continuar:** No hay tiempo para documentar → Mínimo: comentario en package.json/requirements.txt explicando el "por qué". Algo es mejor que nada.

---

## Output de Este Patrón

Al completar este patrón, el Orquestador tiene:
- Justificación clara de la necesidad
- Análisis comparativo de alternativas
- Evaluación de salud y seguridad
- Confirmación de compatibilidad
- Documentación de la decisión

---

## Criterios de Evaluación Rápida

### Green Flags ✓
- Mantenido por organización reconocida
- >1000 estrellas y comunidad activa
- Documentación completa con ejemplos
- Tests automatizados en CI
- Semver estricto
- Respuesta rápida a issues de seguridad

### Red Flags ✗
- Último commit >6 meses
- Issues ignorados
- Sin tests o CI
- Versión 0.x sin roadmap claro
- Dependencias transitivas excesivas
- Licencia restrictiva o incompatible

### Yellow Flags ⚠
- Proyecto de un solo mantenedor
- Documentación solo en código
- Cambios breaking frecuentes
- Comunidad pequeña pero activa

---

## Matriz de Decisión

| Factor | Peso | Candidato A | Candidato B | Build Propio |
|--------|------|-------------|-------------|--------------|
| Resuelve el problema | 25% | | | |
| Salud del proyecto | 20% | | | |
| Seguridad | 20% | | | |
| Compatibilidad | 15% | | | |
| Mantenimiento futuro | 10% | | | |
| Documentación | 10% | | | |
| **Total** | 100% | | | |

---

## Anti-Patrones

| Anti-Patrón | Problema | Solución |
|-------------|----------|----------|
| "Más estrellas = mejor" | Popularidad ≠ calidad | Evaluar todos los criterios |
| Dependencia por feature | Bloat del proyecto | Evaluar costo total |
| Ignorar transitivas | Vulnerabilidades ocultas | Auditar árbol completo |
| "Ya lo arreglarán" | Deuda técnica silenciosa | Evaluar capacidad de respuesta |

---

## Referencias

- Meta-Kata: [`principios-00-meta-kata`](../principios/00-meta-kata.md)
- Patrón relacionado: [`patron-01-code-analysis`](./01-code-analysis.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md)
