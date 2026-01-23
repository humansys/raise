# Análisis Arquitectónico: speckit.util.issues

## 1. Resumen Ejecutivo

El comando `speckit.util.issues` es un utility minimalista que convierte tasks.md en GitHub issues usando la integración MCP (Model Context Protocol). Opera bajo estrictas restricciones de seguridad y validación de remote URL antes de crear issues.

**Patrón arquitectónico clave**: External System Integration con Safety-First Validation.

**Innovación principal**: CAUTION blocks explícitos que enfatizan validación crítica de seguridad - NUNCA crear issues en repos incorrectos.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts.
tools: ['github/github-mcp-server/issue_write']
```

**Patrón**: Tool integration declaration
**Diseño**: Declara explícitamente dependencia en GitHub MCP server.

**Seguridad**: Comando solo funciona si GitHub MCP server está disponible.

### 2.2 Input Processing

**Patrón**: File-based input
- Tasks.md: Source de datos (task list)
- Git remote URL: Validación de target repo

**Estrategia**: NO acepta user arguments para repo - deriva automáticamente de git config.

### 2.3 Outline Structure

**Flujo principal**: 4 pasos con 2 CAUTION blocks críticos

1. **Setup** (prerequisite check con require-tasks)
2. **Extract tasks path** (from script output)
3. **Get Git remote** (validación crítica)
   - **CAUTION**: ONLY PROCEED IF GITHUB URL
4. **Create issues** (for each task via MCP)
   - **CAUTION**: NEVER create in wrong repo

**Característica crítica**: Dos CAUTION blocks explícitos enfatizando security validation.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **Safety-First Validation** | Validar GitHub URL ANTES de cualquier creación | Prevent accidental issue creation en repos equivocados |
| **CAUTION Blocks Explicit** | Dos bloques CAUTION en outline | High-visibility warnings sobre operaciones peligrosas |
| **Single Responsibility** | Solo crea issues; no modifica tasks ni valida contenido | Simplicidad; separation of concerns |
| **MCP Tool Integration** | Usar GitHub MCP server para issue creation | Leverage existing integrations; no reinvent |
| **Automatic Remote Detection** | Derive repo de git config, no user input | Reduce user error; consistency |
| **No Rollback Mechanism** | Una vez creados, issues permanecen | Operación irreversible - validation crítica |
| **Minimal Transformation** | Tasks → Issues directly, no processing | Simplicidad; WYSIWYG |
| **Dependency on Prerequisite** | Requiere tasks.md exista | Fail fast si prerequisito falta |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json --require-tasks --include-tasks` | JSON con path to tasks.md | Ensure tasks exist; get absolute path |
| `git config` | `--get remote.origin.url` | Remote URL string | Validar si es GitHub repo |

**Patrón de integración**: Prerequisite check + git config validation.

**Seguridad**: Doble validación - tasks exist + repo is GitHub.

## 5. Validation Strategy

**Safety-focused validation**:

### Validation 1: Tasks Existence
```
Run check-prerequisites.sh --require-tasks
If tasks.md missing → abort (prerequisite failure)
```

### Validation 2: GitHub URL Validation (CRITICAL)
```
Get remote.origin.url from git config
ONLY PROCEED IF THE REMOTE IS A GITHUB URL
```

**CAUTION block**:
```markdown
> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL
```

### Validation 3: Repo Match (CRITICAL)
```
UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES
THAT DO NOT MATCH THE REMOTE URL
```

**CAUTION block**:
```markdown
> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES
> THAT DO NOT MATCH THE REMOTE URL
```

**Filosofía**: Multiple safety checkpoints antes de operación irreversible.

## 6. Error Handling Patterns

### Pattern 1: Missing Tasks
```
If tasks.md missing → abort with error
Suggest running /speckit.4.tasks
```
**Filosofía**: Fail fast con guidance.

### Pattern 2: Non-GitHub Remote
```
If remote is NOT GitHub URL → HALT EXECUTION
Do NOT proceed to issue creation
```
**Principio**: Explicit validation before destructive operations.

### Pattern 3: No Remote
```
If git config fails (no remote) → abort
Cannot determine target repo
```
**Diseño**: No assumptions; require valid git setup.

### Pattern 4: MCP Server Unavailable
```
If GitHub MCP server not available → command fails
Cannot create issues without tool
```
**Estrategia**: Dependency on external tool - graceful failure.

## 7. State Management

### Input State (Read-Only)
- **tasks.md**: List de tasks con IDs, descriptions, file paths
- **Git remote URL**: Target repo identification

### Intermediate State (None)
- No transformation o processing de tasks
- Direct conversion tasks → issues

### Output State (External System - GitHub)
- **GitHub Issues**: Created in remote repository
- One issue per task en tasks.md

### State Transitions
```
Load tasks → Validate repo is GitHub → For each task → Create GitHub issue
```

**Patrón crítico**: No intermediate state - direct pass-through con validation.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **CAUTION blocks explicit** | High-visibility warnings sobre safety | Verbosity; may be ignored si repetitivo |
| **GitHub-only support** | Leverage existing MCP integration | No funciona con GitLab, Bitbucket, etc. |
| **Automatic remote detection** | Reduce user error | No override si remote setup es complejo |
| **No rollback mechanism** | Simplicidad; issues son baratos de delete manual | No undo si se ejecuta por error |
| **Minimal transformation** | WYSIWYG; tasks → issues directly | No enhancement, formatting, templates |
| **Single responsibility** | Solo crea issues; no otras operaciones | Composability; pero requiere otros comandos para workflow completo |
| **MCP tool dependency** | Leverage external integration | Comando inútil si MCP no disponible |
| **No validation de task content** | Confía en tasks.md correcta (de speckit.4.tasks) | Garbage in, garbage out |

## 9. Comparison with Other Commands

### vs. speckit.4.tasks
- **Tasks**: Genera tasks.md (local file)
- **Issues**: Convierte tasks.md → GitHub issues (external system)
- **Dependency**: Issues consume tasks output

### vs. speckit.6.implement
- **Implement**: Ejecuta tasks localmente
- **Issues**: Exporta tasks a GitHub para tracking externo
- **Use case**: Issues para work tracking; Implement para ejecución

### vs. Other spec-kit commands
- **Todos los demás**: Operan en local filesystem
- **Issues**: Único comando que integra external system (GitHub)

## 10. Learnings for Standardization

### Patrón 1: Safety-First Validation Pattern
**Adoptar**: Validación explícita ANTES de operaciones destructivas/irreversibles.
**Aplicar a**: External system integrations, deployments, data deletion.
**Razón**: Prevent catastrophic errors (wrong repo, wrong environment, etc.).

**Implementation**:
```markdown
1. **Validate Target Environment**:
   - Get target identifier (repo URL, environment name, etc.)
   - Verify it matches expected pattern
   - **HALT** if mismatch

> [!CAUTION]
> ONLY PROCEED IF TARGET MATCHES EXPECTED PATTERN

2. **Execute Operation**:
   - Perform destructive action
   - Log what was done for audit trail
```

### Patrón 2: CAUTION Blocks for Critical Operations
**Adoptar**: Usar bloques CAUTION para operaciones de alto riesgo.
**Aplicar a**: Destructive operations, external integrations, security-sensitive actions.
**Razón**: High-visibility warnings; prevent accidental execution.

**Format**:
```markdown
> [!CAUTION]
> UNDER NO CIRCUMSTANCES [PROHIBITED ACTION]
> ONLY PROCEED IF [VALIDATION CRITERIA]
```

**Placement**: Inmediatamente ANTES del step peligroso.

### Patrón 3: Automatic Environment Detection
**Adoptar**: Derive target environment de config, no user input.
**Aplicar a**: Deployment, integration, environment-specific operations.
**Razón**: Reduce user error; consistency; auditability.

**Implementation**:
```bash
# Detect environment from git config
git config --get remote.origin.url

# Detect environment from kubeconfig
kubectl config current-context

# Detect environment from env vars
echo $ENVIRONMENT
```

### Patrón 4: Single External System Integration
**Adoptar**: Un comando = una external system integration.
**Aplicar a**: Integration commands (GitHub, Slack, JIRA, etc.).
**Razón**: Separation of concerns; easier testing; clear boundaries.

**Anti-pattern**: Comando que crea issues EN GitHub Y Jira Y Linear.
**Pattern**: Comandos separados: `speckit.util.github-issues`, `speckit.util.jira-issues`.

### Patrón 5: MCP Tool Declaration
**Adoptar**: Declarar tool dependencies en frontmatter.
**Aplicar a**: Comandos que usan external tools/APIs.
**Razón**: Explicit dependencies; fail fast si tool unavailable.

**Format**:
```yaml
---
description: [Command description]
tools: ['github/github-mcp-server/issue_write']
---
```

### Patrón 6: No Rollback for Cheap Operations
**Adoptar**: Si operation es barata de undo manually, no implementar rollback.
**Aplicar a**: GitHub issue creation, Slack messages, notifications.
**Razón**: Simplicidad; avoid complexity para edge cases raros.

**Justification**: GitHub issues pueden deletarse fácilmente; implementar rollback automático agrega complejidad sin beneficio proporcional.

### Patrón 7: Minimal Transformation Pass-Through
**Adoptar**: Convertir datos directly sin processing adicional.
**Aplicar a**: Export/import operations entre systems.
**Razón**: WYSIWYG; predictability; simplicidad.

**Example**: Task en tasks.md → Issue en GitHub con misma descripción, sin enhancement.

### Patrón 8: Fail Fast on Missing Prerequisites
**Adoptar**: Validar todos los prerequisites ANTES de comenzar operation.
**Aplicar a**: Todos los comandos con dependencies.
**Razón**: Clear error messages; no partial execution.

**Implementation**:
```markdown
1. Run check-prerequisites.sh --require-tasks --include-tasks
   - If fails → abort with clear message
   - Suggest command to run (e.g., /speckit.4.tasks)
```

### Anti-Patrón 1: User-Specified Target Repo
**Evitar**: Pedir al usuario especificar target repo para issue creation.
**Problema**: User error (typos, wrong repo), security risk (malicious input).
**Solución**: Auto-detect de git config.

### Anti-Patrón 2: Silent Remote Validation
**Evitar**: Validar remote silently sin visibility explícita.
**Problema**: Usuario no sabe qué repo se usará; accidental issue creation.
**Solución**: CAUTION blocks explícitos + confirmation step opcional.

### Anti-Patrón 3: Multi-System Integration
**Evitar**: Un comando que integra múltiples external systems.
**Problema**: Complejidad, difícil testing, unclear boundaries.
**Solución**: One command per external system.

### Anti-Patrón 4: Transformation Without Validation
**Evitar**: Aceptar tasks.md sin validar formato/contenido.
**Problema**: Garbage in, garbage out.
**Solución**: Confiar en que tasks.md viene de speckit.4.tasks (validated).

### Patrón de Arquitectura: External System Integration Pattern
**Concepto**: Pattern estándar para integrar external systems.

**Components**:
1. **Prerequisite Validation**: Ensure input data exists y es válida
2. **Environment Detection**: Auto-detect target environment (repo, cluster, etc.)
3. **Safety Validation**: Verify target matches expected pattern
4. **CAUTION Block**: Explicit warning antes de operation
5. **Operation Execution**: Perform destructive action
6. **Audit Trail**: Log what was done (optional)

**Example flow**:
```markdown
1. Validate input data (tasks.md exists)
2. Detect target (git remote URL)
3. Validate target (is GitHub URL)
   > [!CAUTION] ONLY PROCEED IF GITHUB URL
4. Execute (create issues)
5. Log (report issue URLs created)
```

### Patrón de Diseño: Tool Dependency Declaration
**Concepto**: Declarar explícitamente external tools requeridos.

**Benefits**:
- Fail fast si tool unavailable
- Documentation de dependencies
- Clear error messages
- Integration testing simplificado

**Implementation**:
```yaml
tools: ['github/github-mcp-server/issue_write']
```

**Runtime validation**: Comando verifica tool disponible antes de ejecutar.

### Patrón de Seguridad: Multiple Safety Checkpoints
**Concepto**: Validación en múltiples puntos antes de operation peligrosa.

**Checkpoints para issue creation**:
1. **Checkpoint 1**: Tasks.md exists (prerequisite)
2. **Checkpoint 2**: Git remote detected (environment)
3. **Checkpoint 3**: Remote is GitHub URL (platform)
4. **Checkpoint 4**: Remote matches expected repo (target)

**Enforcement**: HALT si any checkpoint fails.

### Consideración de UX: Clear Error Messages
**Patrón**: Si validation falla, mensaje claro con next action.
**Razón**: User guidance; reduce frustration.

**Examples**:
```
❌ tasks.md not found
→ Run /speckit.4.tasks to generate task list first

❌ Git remote is not a GitHub URL
→ This command only works with GitHub repositories
→ Current remote: gitlab.com/user/repo

❌ No git remote configured
→ Configure remote: git remote add origin <github-url>
```

### Consideración de Seguridad: No Credentials in Command
**Patrón**: Comando no maneja credentials directly.
**Razón**: Security; leverage MCP authentication.
**Implementación**: GitHub MCP server maneja auth; comando solo usa API.

### Consideración de Simplicidad: Minimal Command
**Patrón**: Comando más simple posible - solo validation + operation.
**Razón**: Easy to understand, test, maintain.
**Trade-off**: Menos features (no templates, no formatting, no filtering).

**Philosophy**: Do one thing well - convert tasks to issues con safety validation.

### Patrón de Reporting: Success Confirmation
**Adoptar**: Reportar explícitamente qué se creó después de operation.
**Aplicar a**: Destructive operations, external integrations.
**Razón**: Confirmation, audit trail, debugging.

**Format**:
```markdown
✓ Created 23 GitHub issues in user/repo:
  - Issue #145: [T001] Create project structure
  - Issue #146: [T002] Install dependencies
  - ...
  - Issue #167: [T023] Write documentation

View all issues: https://github.com/user/repo/issues
```

### Consideración de Idempotencia: No Protection
**Decisión**: Comando NO es idempotent - cada run crea nuevos issues.
**Razón**: Simplicidad; GitHub permite duplicates; deletion es fácil.
**Trade-off**: Usuario debe verificar antes de ejecutar múltiples veces.

**Alternative pattern** (no implementado): Track created issues para evitar duplicates.
