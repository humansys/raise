# Glosario Esencial de RaiSE

Los 5 conceptos que necesitas para empezar a usar el framework RaiSE. Si estás comenzando (Stage 0), este glosario mínimo te permite arrancar sin leer los ~35 términos del glosario completo.

---

## Orquestador

Tú. El humano que dirige el trabajo del agente de IA.

Defines **QUÉ** construir (especificas requisitos), y el agente propone **CÓMO** hacerlo (genera código). El Orquestador mantiene ownership del sistema: valida outputs, toma decisiones arquitectónicas, y diseña el contexto en el que el agente opera.

**Ejemplo**: Cuando ejecutas `/speckit.specify` y describes tu feature, estás actuando como Orquestador - defines el qué, no el cómo.

---

## Spec

Documento que describe lo que quieres construir.

Es tu "contrato" con el agente: especifica requisitos funcionales, criterios de aceptación, y success criteria. La Spec es la fuente de verdad sobre QUÉ debe hacer el sistema, sin detalles de CÓMO implementarlo.

**Ejemplo**: El archivo `spec.md` que generaste con `/speckit.specify` es tu Spec. Describe el feature en lenguaje natural, sin mencionar frameworks o código.

---

## Agent

La IA que ejecuta tus instrucciones.

Puede ser Claude Code, GitHub Copilot, Cursor, Windsurf, u otro sistema de IA. El agente lee tu Spec, genera código, y ejecuta tareas bajo tu dirección. No toma decisiones arquitectónicas autónomas - tú eres quien decide.

**Ejemplo**: Claude Code ejecutando los comandos de spec-kit (como `/speckit.plan` o `/speckit.implement`) es el agente en acción.

---

## Validation Gate

Checkpoint de calidad. Si no lo pasas, no avanzas.

Cada fase del workflow tiene su propio gate con criterios específicos que deben cumplirse antes de proceder. Los gates previenen que errores o ambigüedades se propaguen a etapas posteriores.

**Ejemplo**: Antes de ejecutar `/speckit.plan`, tu spec debe pasar el gate de "especificación completa" - sin requisitos ambiguos o contradicciones.

---

## Constitution

Principios inmutables del proyecto. El agente nunca los viola.

Es el documento de mayor jerarquía en tu repositorio: define valores, restricciones, y decisiones arquitectónicas fundamentales. La Constitution raramente cambia y todo lo demás (specs, código, ADRs) debe alinearse con ella.

**Ejemplo**: `CLAUDE.md` y `.specify/memory/constitution.md` en tu repositorio contienen las reglas que Claude Code siempre respeta al generar código o diseñar arquitectura.

---

*Para el glosario completo con ~35 términos, consulta [20-glossary-v2.1.md](./20-glossary-v2.1.md)*
