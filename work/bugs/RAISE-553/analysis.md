# Bug Analysis: RAISE-553

## Root Cause (5 Whys — S)

Problem → backlog commands muestran traceback crudo
Why1 → excepciones del adapter no se atrapan en 7 de 9 comandos
Why2 → `create`, `transition`, `update`, `link`, `comment`, `search`, `batch-transition`
         llaman pm.method() sin try/except
Why3 → get/get-comments sí tienen try/except, pero fueron escritos después — inconsistencia
Why4 → no hay política de error handling a nivel de CLI group, cada comando decide
Root cause → el patrón de manejo de errores se aplicó parcialmente; no existe guardrail
             a nivel de backlog_app que capture excepciones de adapter por defecto

## Commands affected (no error handling)
- create       → pm.create_issue()
- transition   → pm.transition_issue()
- update       → pm.update_issue()
- link         → pm.link_issues()
- comment      → pm.add_comment()
- search       → pm.search()
- batch-transition → pm.batch_transition()

## Commands already correct
- get          → try/except Exception → [red]Error:[/red] {exc}
- get-comments → try/except Exception → [red]Error:[/red] {exc}

## Fix Approach

Agregar try/except Exception a los 7 comandos afectados, siguiendo el patrón existente:
    try:
        ref = pm.some_call(...)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
