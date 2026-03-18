# Retrospective: RAISE-552

## Summary
- Root cause: `McpJiraAdapter.search()` enviaba el query raw como JQL sin normalización
- Fix approach: `_to_jql()` static method — 3 casos: issue key, JQL explícito, texto plano

## Heutagogical Checkpoint
1. Learned: El adapter JQL tenía ya precedente de sanitización (RAISE-435 `\!` → `!`) pero no tenía el caso más básico: texto plano. El boundary entre "responsabilidad del caller" y "responsabilidad del adapter" no estaba bien definido.
2. Process change: Ninguno — el flujo RED-GREEN fue limpio y directo.
3. Framework improvement: El scope de RAISE-552 fue correcto como XS — el análisis por traceback directo fue suficiente sin Ishikawa.
4. Capability gained: Patrón `_to_jql()` ahora establecido — futuros adapters PM deben incluir normalización similar.

## Patterns
- Added: none (fix demasiado puntual para patrón generalizable)
- Reinforced: none evaluated
