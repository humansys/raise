# Retrospective: RAISE-572

## Summary
- Root cause: instrucción ambigua en SKILL.md permitía paths específicos por omisión — el AI siempre infiere "verificar lo que toqué"
- Fix approach: regla explícita que prohíbe paths específicos y exige el comando global del manifest

## Heutagogical Checkpoint
1. **Learned:** Las skills son prompts — una instrucción ambigua produce comportamiento inconsistente. "Resolve from manifest" sin especificar la forma no es suficiente guardrail.
2. **Process change:** Al escribir skills, toda instrucción que involucre comandos debe especificar forma Y restricciones, no solo fuente.
3. **Framework improvement:** Sería útil un lint de skills que detecte instrucciones sin forma explícita en verification commands.
4. **Capability gained:** Entendimiento de que las skills necesitan el mismo rigor de especificación que el código — ambigüedad en prompts = bugs en comportamiento.

## Patterns
- Added: none — el insight ya aplica a skill authoring en general
- Reinforced: none evaluated
