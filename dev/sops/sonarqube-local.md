# SOP: SonarQube Local Analysis

> Standard Operating Procedure para análisis estático local con SonarQube Community
> Version: 1.0
> Date: 2026-03-11
> Status: Active

---

## Propósito

Correr análisis estático de código (SAST) localmente sin depender de SonarCloud ni de CI. Permite ver issues en terminal antes de hacer push.

**Qué detecta:**
- Bugs de lógica (ramas imposibles, parámetros sin usar)
- Code smells (complejidad cognitiva, literales duplicados)
- Security hotspots (taint analysis dentro de un archivo)

**Qué NO detecta** (requiere tiers pagados o herramientas externas):
- Vulnerabilidades en dependencias → usar Snyk
- Taint analysis cross-archivo → SonarQube Developer Edition
- Secrets en git history → ver SOP de gitleaks (pendiente)

---

## Dependencias

| Herramienta | Para qué | Instalación |
|-------------|----------|-------------|
| Docker | Servidor SonarQube + scanner | https://docs.docker.com/engine/install/ |
| `sonar` CLI | Ver issues en terminal | Ver sección de instalación abajo |
| `LOCAL_SONAR_TOKEN` | Autenticación | Ver sección de setup abajo |

---

## Instalación (una sola vez por máquina)

### 1. Instalar sonar CLI

```bash
curl -o- https://raw.githubusercontent.com/SonarSource/sonarqube-cli/refs/heads/master/user-scripts/install.sh | bash
```

Abre una terminal nueva para que el PATH se actualice.

### 2. Levantar el servidor SonarQube

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

Espera ~1 minuto a que esté listo:

```bash
curl -s http://localhost:9000/api/system/status
# Esperar: {"status":"UP",...}
```

### 3. Generar token

1. Abre http://localhost:9000
2. Login: `admin` / `admin` (te pedirá cambiar la contraseña)
3. My Account → Security → Generate Token → copia el token

### 4. Configurar token

Agrega a `~/.env`:

```bash
LOCAL_SONAR_TOKEN=squ_<tu-token>
```

El `~/.env` se carga automáticamente en cada terminal via `.bashrc`/`.zshrc`.

### 5. Login con el CLI

```bash
sonar auth login -s http://localhost:9000 -t $LOCAL_SONAR_TOKEN
```

---

## Uso diario

### Levantar el servidor (si reiniciaste la máquina)

```bash
docker start sonarqube
```

### Escanear el código

Desde la raíz del repo:

```bash
docker run --rm --network host \
  -e SONAR_TOKEN=$LOCAL_SONAR_TOKEN \
  -e SONAR_HOST_URL=http://localhost:9000 \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli:latest \
  -Dsonar.scm.disabled=true
```

> **Nota:** `-Dsonar.scm.disabled=true` es necesario porque el repo usa git worktrees.
> El scan tarda ~15 segundos.

### Ver issues

```bash
# Todos los issues
sonar list issues -p humansys-demos_raise-commons --format table

# Solo críticos
sonar list issues -p humansys-demos_raise-commons --format table --severity CRITICAL

# Solo bugs
sonar list issues -p humansys-demos_raise-commons --format table --type BUG

# Solo vulnerabilidades
sonar list issues -p humansys-demos_raise-commons --format table --type VULNERABILITY
```

---

## Comparar con SonarCloud

Para ver los issues del análisis en CI (SonarCloud), apunta el CLI a SonarCloud:

```bash
sonar auth login -s https://sonarcloud.io -t $SONAR_TOKEN --org test-raise
sonar list issues -p humansys-demos_raise-commons --format table
```

Para volver a local:

```bash
sonar auth login -s http://localhost:9000 -t $LOCAL_SONAR_TOKEN
```

---

## Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| `Unable to open Git repository` | Repo es un git worktree | Agregar `-Dsonar.scm.disabled=true` al scan |
| `LOCAL_SONAR_TOKEN is not set` | No está en ~/.env | Agregar y abrir terminal nueva |
| `Failed to query server` | Servidor no está corriendo | `docker start sonarqube` |
| `host.docker.internal` no resuelve | Solo funciona en macOS/Windows | Usar `--network host` en Linux |
