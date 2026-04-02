# Bug Scope: RAISE-553

WHAT:      Errores del adapter de backlog muestran traceback Python completo con rich panel
WHEN:      Cualquier excepción en: create, transition, update, link, comment, search, batch-transition
WHERE:     src/raise_cli/cli/commands/backlog.py — 7 comandos sin try/except
EXPECTED:  Error limpio: "[red]Error:[/red] {mensaje}" + exit code 1
Done when: Todos los comandos de backlog atrapan excepciones de adapter y muestran
           mensaje limpio sin traceback. get/get-comments ya lo hacen correctamente.

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
