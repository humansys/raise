# RAISE-566 — Session start pierde el contexto de la sesión anterior

**Estado:** Resuelto · **Severidad:** Mayor · **Commit:** `f568ed84`

---

## ¿Qué estaba pasando?

Cada vez que un desarrollador arrancaba una nueva sesión con `rai session start --context`, el CLI mostraba "no previous session state" aunque la sesión anterior había cerrado sin errores. Todo el trabajo acumulado durante la jornada anterior desaparecía: el resumen de lo que se hizo, las decisiones pendientes, y el prompt de continuidad que el propio desarrollador había escrito para sí mismo al cerrar.

El efecto era que cada sesión empezaba en blanco. El desarrollador tenía que recordar manualmente dónde había quedado, revisar el historial de git, o simplemente continuar a ciegas. El problema era completamente reproducible — no era intermitente ni dependía de condiciones especiales — ocurría en cada ciclo close → start normal.

---

## El ciclo del desarrollador

Al final del día, el desarrollador cierra su sesión. Al día siguiente ejecuta `rai session start --context` esperando ver dónde quedó.

**Con el bug:**

```
$ rai session start --context

Session: SES-N

Work:     (no previous session state)
Focus:    (none)
Signals:  None
```

**Después del fix:**

```
$ rai session start --context

Session: SES-N

Work:     EPIC-1 → S1.2 My Feature, phase: implement
Focus:    Continue Task 3

Session Narrative:
  ## Decisions
  - Decision A taken yesterday
  ## Branch State
  - story/s1.2/my-feature, 2 commits ahead of dev

Next session:
  S1.2 — Task 3 pending. Pick up from where we left off.

Signals:  None
```

El archivo de estado existía y estaba bien escrito. No había ningún error visible — el CLI arrancaba normalmente. Solo faltaba el contenido.

---

## Por qué pasó

Para entender el bug hay que saber cómo el CLI organiza el estado de sesión en disco. Cuando se cierra una sesión, el estado se guarda en un archivo plano dentro del proyecto:

```
.raise/rai/personal/session-state.yaml
```

Cuando arranca la siguiente sesión, el CLI necesita hacer dos cosas: archivar ese estado en el historial de la sesión anterior, y leerlo para construir el bundle de contexto que ve el desarrollador.

El problema era el **orden** en que estas dos operaciones ocurrían dentro de la función `start()`.

Primero se ejecutaba `migrate_flat_to_session()`. Esta función tomaba el archivo `session-state.yaml` y lo **movía** a su ubicación histórica:

```
sessions/SES-{N-1}/state.yaml
```

Correcto hasta ahí. El problema venía justo después: `load_session_state()` intentaba leer el estado usando el ID de la sesión **nueva** (`SES-{N}`), buscando un archivo en `sessions/SES-{N}/state.yaml`. Ese directorio no existía todavía. El archivo con la información real ya había sido movido a `SES-{N-1}/`, y la función regresaba `None`.

En términos simples: **el CLI archivaba el documento antes de leerlo**.

Lo que hace más interesante este bug es que el diseño original no era irracional. `migrate_flat_to_session` y `load_session_state` fueron diseñadas y revisadas por separado, y cada una tiene sentido en aislamiento. El error estaba en la composición: nadie trazó qué pasaría con el lector que operaba justo en la misma ventana de tiempo que el movimiento.

---

## Cómo se resolvió

El fix fue pequeño — tres líneas netas de cambio. La solución fue capturar el estado del archivo plano en una variable **antes** de ejecutar la migración. Así, la migración puede mover el archivo sin consecuencias, porque la información ya fue leída.

```python
# Antes: la migración movía el archivo antes de que alguien lo leyera
migrate_flat_to_session(project, session_id)
state = load_session_state(project, session_id)  # → None, el archivo ya no está

# Después: leer primero, mover después
prev_state = load_session_state(project)          # lee el archivo plano
migrate_flat_to_session(project, session_id)      # ahora puede mover libremente
# prev_state tiene lo que necesitamos
```

El fix se verificó con un test de regresión que simula el ciclo completo close → start y comprueba que `current_work`, `narrative`, `next_session_prompt` y `pending` estén presentes en el bundle de contexto.

---

## Lección

Cuando una función mueve o transforma un recurso compartido, hay que auditar todos los lectores que operan en la misma ventana de tiempo — especialmente en la función que los invoca. No basta con que cada función tenga sentido por separado; el orden de composición importa.

Este patrón se capturó en el framework como **PAT-E-425** para que no se repita en diseños futuros.
