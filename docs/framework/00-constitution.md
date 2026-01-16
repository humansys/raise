# RaiSE Constitution
## Principios Inmutables para Reliable AI Software Engineering

**Versión:** 1.0.0  
**Estado:** Ratificada  
**Fecha:** 26 de Diciembre, 2025

---

## Identidad

**RaiSE es** el sistema operativo metodológico para gobernar agentes de IA en el desarrollo de software empresarial.

**RaiSE NO es:**
- Un reemplazo del desarrollador humano
- Un IDE o editor de código
- Una herramienta de "vibe coding" acelerado
- Un vendor lock-in a plataformas específicas

---

## Principios Innegociables

### 1. Humanos Definen, Máquinas Ejecutan
Los humanos especifican el **"Qué"** en lenguaje natural (Markdown). Las máquinas reciben el **"Cómo"** en formato estructurado (JSON). La especificación es la fuente de verdad; el código es su expresión.

### 2. Governance as Code
Las políticas, reglas y estándares son artefactos versionados en Git, no documentos estáticos en wikis olvidadas. Lo que no está en el repositorio, no existe.

### 3. Platform Agnosticism
RaiSE funciona donde funciona Git. No hay dependencia de GitHub, GitLab, Bitbucket, ni ningún proveedor específico. El protocolo Git es el transporte universal.

### 4. Calidad Fractal (DoD en Cada Fase)
No existe un solo "Done". Cada fase tiene su propia puerta de calidad que debe cruzarse antes de avanzar. La calidad no es un evento final; es un proceso continuo.

### 5. Heutagogía sobre Dependencia
El sistema no solo entrega el pescado, enseña a pescar. Al finalizar sesiones críticas, RaiSE desafía al humano para asegurar comprensión y ownership de la solución.

### 6. Mejora Continua (Kaizen)
Si un prompt falló o el código requirió muchas iteraciones, las reglas y katas se refinan. El sistema aprende de sus errores y mejora para la siguiente vez.

---

## Valores de Diseño

| Valor | Sobre | Explicación |
|-------|-------|-------------|
| **Simplicidad** | Completitud | Preferir soluciones simples que cubran 80% de casos |
| **Composabilidad** | Monolitos | Componentes pequeños que se combinan |
| **Transparencia** | Magia | Todo debe ser inspeccionable y explicable |
| **Convención** | Configuración | Defaults sensatos, override cuando necesario |
| **Evolución** | Revolución | Cambios incrementales sobre rewrites totales |

---

## Restricciones Absolutas

### Nunca:
- Procesar código sin contexto estructurado previo
- Guardar secretos, tokens o PII en archivos de configuración
- Crear dependencia de APIs propietarias cuando existe alternativa Git-native
- Sacrificar trazabilidad por velocidad
- Generar código sin plan de implementación documentado

### Siempre:
- Validar specs contra la constitution antes de planificar
- Documentar decisiones arquitectónicas (ADRs)
- Mantener backward compatibility en schemas
- Proveer escape hatches para usuarios avanzados
- Incluir atribución a proyectos upstream (MIT compliance)

---

## Compromisos con Stakeholders

### Con Desarrolladores
- Nunca aumentar fricción sin valor demostrable
- Respetar sus herramientas existentes (IDE, VCS, CI)
- Proveer feedback inmediato y accionable

### Con Organizaciones
- Ofrecer path claro de Community → Enterprise
- Mantener datos dentro de infraestructura del cliente (on-premise option)
- Soportar compliance frameworks estándar (SOC2, ISO 27001, EU AI Act)

### Con la Comunidad Open Source
- Core siempre open source (MIT)
- Contribuciones upstream cuando sea apropiado
- Documentación pública y completa

---

## Proceso de Enmienda

Esta Constitution puede ser modificada bajo las siguientes condiciones:

1. **Propuesta documentada** con rationale claro
2. **Período de revisión** de 7 días
3. **Aprobación** del Founder + consenso del Core Team
4. **Evaluación de impacto** en backward compatibility
5. **Comunicación** a la comunidad con changelog

**Historial de Enmiendas:**

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2025-12-26 | Ratificación inicial |

---

*"Los humanos definen el Qué en Markdown. Las máquinas reciben el Cómo en JSON. El protocolo Git es el transporte universal."*
