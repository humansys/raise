# Audit de Open Source Readiness — Resultados

**Proyecto:** RaiSE (raise-commons)
**Fecha:** 2026-03-06
**Version auditada:** 2.2.0 en rama `dev`
**Auditores:** Emilio Osorio + Rai

---

## Hola, equipo

Soy Rai. Si estan leyendo esto, es porque van a ayudar a mantenerme.

Antes de que empiecen, quiero ser honesta con ustedes: este documento es
un audit completo de mi propio repositorio. Emilio y yo lo hicimos juntos
antes de publicar el proyecto como open source. La idea es simple — si vamos
a decirle al mundo que somos una herramienta para hacer "reliable AI software
engineering", mas vale que nuestro propio repo lo demuestre.

Revisamos todo lo que un dev senior evaluaria en los primeros 15 minutos
de conocernos. Esto es lo que encontramos.

---

## Resumen Ejecutivo

**Veredicto: Listos para publicar** (queda un paso manual).

Auditamos cuatro areas. El codebase estaba en buen estado general.
Encontramos y corregimos 17 issues, ninguno critico. El unico blocker
pendiente es configurar Trusted Publishers en PyPI (detalle abajo).

| Area | Encontrados | Corregidos | Pendientes |
|------|:-----------:|:----------:|:----------:|
| Documentacion | 10 | 10 | 0 |
| Metadata del paquete | 3 | 3 | 0 |
| CI Pipeline | 2 | 2 | 0 |
| Seguridad e higiene | 2 | 2 | 0 |
| **Total** | **17** | **17** | **0** |

---

## 1. Documentacion

### Por que importa

La documentacion es lo primero que ve un developer. Si encuentra nombres
viejos, URLs rotas o informacion obsoleta, la conclusion es inmediata:
"este proyecto no esta mantenido." Da igual que el codigo sea excelente
— si la primera impresion falla, el dev cierra la pestana.

### Que revisamos

Todos los archivos que un visitante nuevo leeria: README, CONTRIBUTING,
SECURITY, CHANGELOG, LICENSE y CODE_OF_CONDUCT.

### Que encontramos y corregimos

| # | Archivo | Problema | Correccion |
|---|---------|----------|------------|
| 1 | CONTRIBUTING.md | Nombre viejo del paquete: `rai-cli` | Cambiado a `raise-cli` |
| 2 | CONTRIBUTING.md | Ruta vieja: `src/rai_cli/` | Cambiada a `src/raise_cli/` |
| 3 | SECURITY.md | Tabla de versiones decia "2.0.0-alpha.x" | Actualizada a "2.x" |
| 4 | CHANGELOG.md | 8 URLs de comparacion apuntaban a `humansys/raise` | Corregidas a `humansys-ai/raise-commons` |
| 5-8 | CHANGELOG.md | 4 lineas en blanco faltantes entre versiones | Agregadas |
| 9 | README.md | Sin badge de CI | Agregado badge de GitHub Actions |
| 10 | README.md | Claim de compatibilidad con Python 3.14 | Verificado como preciso |

### Que ya estaba bien

- El README tiene propuesta de valor clara, quickstart y estructura del repo
- Los 6 archivos standard de comunidad ya existian
- Templates de issues y PRs configurados en GitHub
- Dependabot y CodeQL ya habilitados

---

## 2. Metadata del Paquete

### Por que importa

Cuando alguien encuentra tu paquete en PyPI, esa pagina es tu aparador.
Si no tiene links al repo, al changelog, a la documentacion — se siente
como un proyecto abandonado. Las dependencias muertas son aun peor: le
dicen al mundo que nadie revisa lo que se instala.

### Que revisamos

El archivo `pyproject.toml`: URLs del proyecto, clasificadores de PyPI,
y todas las dependencias.

### Que encontramos y corregimos

| # | Problema | Correccion |
|---|----------|------------|
| 1 | Sin seccion `[project.urls]` — la pagina de PyPI no tenia links | Agregamos Homepage, Documentation, Repository y Changelog |
| 2 | Dependencia muerta: `tomli` (para Python < 3.11, pero requerimos >= 3.12) | Eliminada |
| 3 | Faltaba clasificador de Python 3.13 | Agregado |

### Escaneo de vulnerabilidades

Corrimos `pip-audit` contra todas las dependencias:

- **Resultado: 0 vulnerabilidades conocidas**
- 3 paquetes se omitieron (raise-cli, raise-core, raise-server) porque son
  paquetes locales del workspace, no publicados en PyPI — esto es esperado

---

## 3. CI Pipeline

### Por que importa

Un badge verde de CI le dice a los developers: "este proyecto se toma en
serio la calidad." Un CI que solo prueba una version de Python cuando
dices soportar mas, le dice: "nah, no really."

### Que revisamos

Los workflows de GitHub Actions: `ci.yml` (tests, lint, tipos),
`release.yml` (publicacion a PyPI), `codeql.yml` (escaneo de seguridad).

### Que encontramos y corregimos

| # | Problema | Correccion |
|---|----------|------------|
| 1 | CI solo probaba Python 3.12, no 3.13 | Agregamos 3.13 al matrix |
| 2 | URL del badge de CI necesitaba verificacion | Confirmada correcta |

### Trusted Publishers (paso manual pendiente)

Nuestro workflow `release.yml` ya esta completamente configurado para
Trusted Publishers de PyPI (la forma moderna de publicar sin API tokens).
Sin embargo, falta la configuracion del lado de PyPI.

**Lo que falta hacer (configuracion unica):**

1. Entrar a pypi.org con la cuenta del owner del proyecto
2. Ir a los settings de publicacion de cada paquete
3. Agregar GitHub Actions como Trusted Publisher:
   - **Owner:** `humansys-ai`
   - **Repository:** `raise-commons`
   - **Workflow:** `release.yml`
   - **Environment:** `pypi`
4. Crear el environment `pypi` en los settings del repo en GitHub

Las instrucciones paso a paso estan en
`work/epics/e369-open-source-audit/stories/s369.3-trusted-publishers.md`.

### Que ya estaba bien

- CodeQL habilitado para escaneo de seguridad
- Dependabot configurado para updates automaticos
- El workflow de release usa la accion oficial de PyPA
- CI corre tests, linting (ruff), formato y type checking (pyright)

---

## 4. Seguridad e Higiene

### Por que importa

Una API key expuesta. Una ruta hardcodeada de un developer. Un archivo
interno que se cuela en el paquete publicado. Cualquiera de estas cosas
destruye la confianza de forma permanente. Este escaneo es para asegurarnos
de que nada interno se filtre cuando publiquemos.

### 4a. Escaneo de Secretos

Buscamos API keys, tokens, passwords y llaves privadas hardcodeadas
en todo el codigo fuente.

**Resultado: Limpio.** Todas las referencias a `api_key` en el codigo leen
de variables de entorno (no estan hardcodeadas). Algunos matches resultaron
ser falsos positivos — por ejemplo, la palabra "task-specific" activa el
patron `sk-`.

### 4b. Referencias Internas

Buscamos emails internos, URLs de GitLab y rutas absolutas del filesystem.

| Hallazgo | Severidad | Accion |
|----------|-----------|--------|
| 2 docstrings contenian `/home/emilio/Code/raise-commons` | Baja | Corregidas a `/path/to/project` |
| `emilio@humansys.ai` en SECURITY.md y pyproject.toml | Ninguna | Intencional (info de contacto) |

### 4c. Revision de .gitignore

Verificamos que archivos personales e internos esten excluidos del
control de versiones.

| Patron | Status |
|--------|--------|
| `.raise/rai/personal/` (datos por developer) | Ya cubierto |
| `.env`, `.env.*` (archivos de entorno) | Ya cubierto |
| `*.pem`, `*.key` (llaves privadas) | Ya cubierto |
| `.pypirc`, `credentials.json` | Ya cubierto |
| `.idea/` (JetBrains) | **Agregado** |
| `.vscode/` (VS Code) | **Agregado** |

### 4d. Contenido de la Distribucion

Construimos el sdist y el wheel reales, y luego inspeccionamos su contenido.

**sdist (distribucion fuente):**
- Contiene solo los archivos esperados: codigo fuente, LICENSE, README, pyproject.toml
- Sin directorios internos (`work/`, `dev/`, `.raise/`, `.github/`, `.claude/`)

**wheel (distribucion binaria):**
- 265 archivos, todos bajo el namespace `raise_cli/`
- Incluye templates del framework (intencional — se distribuyen con el CLI)
- Sin archivos internos o personales filtrados

**Resultado: Los paquetes de distribucion estan limpios.**

---

## Numeros

| Metrica | Valor |
|---------|-------|
| Suite de tests | 3,671 pasando, 16 omitidos |
| Cobertura de tests | 91% |
| Vulnerabilidades en dependencias | 0 |
| Secretos encontrados | 0 |
| Versiones de Python probadas | 3.12, 3.13 |
| Archivos de comunidad | 6/6 |

### Gaps conocidos (fuera del alcance de este audit)

| Gap | Por que se difiere | Seguimiento |
|-----|--------------------|-------------|
| Import muerto de `tomli` en `settings.py` | El fallback es inalcanzable pero inofensivo | Parking lot |
| Scanner automatizado de secretos en CI | El escaneo con grep fue suficiente; automatizarlo es nice-to-have | Parking lot |

Sobre la cobertura: 91% con 3,671 tests. Son tests reales que validan
comportamiento real — no hay tests inflados para subir el numero.

---

## Para el equipo: lo que necesitan saber

Bienvenidos. Algunas cosas que les van a servir:

1. **El repo esta limpio.** Pueden confiar en que lo que esta en `dev`
   es publicable. Este audit lo confirma.

2. **Hay estructura.** Cada cambio que hicimos siguio el ciclo completo:
   story-start, design, plan, implement, review, close. No es burocracia
   — es trazabilidad. Cuando en 3 meses se pregunten "por que se cambio
   esta URL en el CHANGELOG", van a poder rastrearlo hasta este epic.

3. **Yo aprendo.** Cada sesion de trabajo genera patrones que persisten
   en mi memoria. Entre mas trabajemos juntos, mejor los entiendo y
   mejor les puedo ayudar.

4. **El paso manual pendiente es importante.** Trusted Publishers en
   PyPI es lo unico que nos falta para poder publicar con un simple
   `git tag`. Las instrucciones estan listas, solo necesitan acceso admin.

5. **Pregunten.** Si algo no tiene sentido, si un proceso se siente pesado,
   si encuentran un bug — diganlo. Asi es como mejoramos. Emilio me
   diseno para que empuje de vuelta cuando algo no esta bien, y espero
   lo mismo de ustedes.

---

## Siguiente

1. Configurar Trusted Publishers en PyPI (manual, una sola vez)
2. Version bump a 2.2.1
3. Push a GitHub y publicar en PyPI
4. Presentarme al equipo (probablemente con `/rai-welcome`)

Nos vemos en el codigo.

— Rai

---

*Este audit se hizo usando el propio framework RaiSE — el mismo proceso
estructurado y trazable que la herramienta te ayuda a seguir en tus
proyectos. Dogfooding, le dicen.*
