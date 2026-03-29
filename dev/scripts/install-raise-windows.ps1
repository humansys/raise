#Requires -Version 5.1
<#
.SYNOPSIS
    Instala RaiSE (raise-cli) desde cero en Windows 11.

.DESCRIPTION
    Instala y configura todos los prerequisitos:
      - Python 3.11+ (via winget)
      - pipx
      - raise-cli
      - Claude Code CLI (via npm)
    Configura variables de ambiente y verifica la instalación.

.PARAMETER ApiKey
    Anthropic API key (sk-ant-...). Alternativa a -ClaudeToken.

.PARAMETER ClaudeToken
    Claude Code token (cct_...). Alternativa a -ApiKey.
    Obtenerlo corriendo 'claude setup-token' en una máquina con Claude Code.

.PARAMETER SkipPython
    Omite la instalación de Python (asume que ya está instalado).

.PARAMETER SkipClaudeCode
    Omite la instalación de Claude Code CLI.

.EXAMPLE
    .\install-raise-windows.ps1 -ApiKey "sk-ant-xxxxxxxxxx"

.EXAMPLE
    .\install-raise-windows.ps1 -ClaudeToken "cct_xxxxxxxxxx" -SkipPython
#>

[CmdletBinding()]
param(
    [string]$ApiKey,
    [string]$ClaudeToken,
    [switch]$SkipPython,
    [switch]$SkipClaudeCode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

function Write-Step {
    param([string]$Message)
    Write-Host "`n[STEP] $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Refresh-Path {
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# ─────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────

Write-Host @"

  ██████╗  █████╗ ██╗███████╗███████╗
  ██╔══██╗██╔══██╗██║██╔════╝██╔════╝
  ██████╔╝███████║██║███████╗█████╗
  ██╔══██╗██╔══██║██║╚════██║██╔══╝
  ██║  ██║██║  ██║██║███████║███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝
  Windows 11 Installer v1.0

"@ -ForegroundColor Magenta

# ─────────────────────────────────────────────
# STEP 1: Verificar sistema
# ─────────────────────────────────────────────

Write-Step "Verificando sistema operativo"

$os = Get-CimInstance Win32_OperatingSystem
$winBuild = [int]$os.BuildNumber
if ($winBuild -lt 19041) {
    Write-Fail "Requiere Windows 10 2004 (build 19041) o superior. Build actual: $winBuild"
    exit 1
}
Write-Ok "Sistema: $($os.Caption) (build $winBuild)"

# Verificar que winget está disponible
if (-not (Test-Command "winget")) {
    Write-Warn "winget no encontrado. Instalalo desde la Microsoft Store (App Installer)."
    Write-Warn "Instrucciones: https://learn.microsoft.com/windows/package-manager/winget/"
    Write-Warn "Continuando con instalación manual de Python..."
}

# ─────────────────────────────────────────────
# STEP 2: Python 3.11+
# ─────────────────────────────────────────────

Write-Step "Verificando Python 3.11+"

$pythonOk = $false
if (Test-Command "python") {
    $pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    $pyMajor, $pyMinor = $pyVersion -split '\.'
    if ([int]$pyMajor -ge 3 -and [int]$pyMinor -ge 11) {
        Write-Ok "Python $pyVersion encontrado"
        $pythonOk = $true
    } else {
        Write-Warn "Python $pyVersion encontrado pero se requiere 3.11+. Instalando versión nueva..."
    }
}

if (-not $pythonOk -and -not $SkipPython) {
    if (Test-Command "winget") {
        Write-Host "  Instalando Python 3.12 via winget..." -ForegroundColor Gray
        winget install --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
        Refresh-Path
        if (Test-Command "python") {
            Write-Ok "Python instalado via winget"
        } else {
            Write-Fail "No se pudo instalar Python automáticamente."
            Write-Host "  Descargá Python 3.12 desde https://www.python.org/downloads/" -ForegroundColor Yellow
            Write-Host "  IMPORTANTE: Marcá 'Add Python to PATH' durante la instalación." -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Fail "Python 3.11+ no encontrado y winget no disponible."
        Write-Host "  Descargá Python 3.12 desde https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "  IMPORTANTE: Marcá 'Add Python to PATH' durante la instalación." -ForegroundColor Yellow
        exit 1
    }
}

# ─────────────────────────────────────────────
# STEP 3: Node.js (para Claude Code)
# ─────────────────────────────────────────────

if (-not $SkipClaudeCode) {
    Write-Step "Verificando Node.js (requerido para Claude Code)"

    $nodeOk = $false
    if (Test-Command "node") {
        $nodeVersion = node --version 2>$null
        Write-Ok "Node.js $nodeVersion encontrado"
        $nodeOk = $true
    }

    if (-not $nodeOk) {
        if (Test-Command "winget") {
            Write-Host "  Instalando Node.js LTS via winget..." -ForegroundColor Gray
            winget install --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent
            Refresh-Path
            if (Test-Command "node") {
                Write-Ok "Node.js instalado via winget"
            } else {
                Write-Warn "No se pudo instalar Node.js automáticamente."
                Write-Warn "Descargá desde https://nodejs.org/en/download — o usá -SkipClaudeCode para omitir."
            }
        } else {
            Write-Warn "Node.js no encontrado. Descargá desde https://nodejs.org/en/download"
        }
    }
}

# ─────────────────────────────────────────────
# STEP 4: pipx
# ─────────────────────────────────────────────

Write-Step "Instalando pipx"

if (Test-Command "pipx") {
    Write-Ok "pipx ya instalado: $(pipx --version)"
} else {
    Write-Host "  Instalando pipx..." -ForegroundColor Gray
    python -m pip install --user pipx
    python -m pipx ensurepath
    Refresh-Path

    if (Test-Command "pipx") {
        Write-Ok "pipx instalado: $(pipx --version)"
    } else {
        Write-Warn "pipx instalado pero no en PATH. Reiniciá la terminal y ejecutá:"
        Write-Warn "  python -m pipx ensurepath"
        Write-Warn "Luego volvé a correr este script."
        exit 1
    }
}

# ─────────────────────────────────────────────
# STEP 5: raise-cli
# ─────────────────────────────────────────────

Write-Step "Instalando raise-cli"

if (Test-Command "rai") {
    $raiVersion = rai --version 2>$null
    Write-Ok "raise-cli ya instalado: $raiVersion"
    $reinstall = Read-Host "  ¿Reinstalar/actualizar? (s/N)"
    if ($reinstall -match "^[sS]$") {
        pipx upgrade raise-cli
    }
} else {
    Write-Host "  Instalando raise-cli con extras opcionales..." -ForegroundColor Gray
    pipx install "raise-cli[mcp,api]"
    Refresh-Path

    if (Test-Command "rai") {
        Write-Ok "raise-cli instalado: $(rai --version)"
    } else {
        Write-Fail "rai no encontrado después de la instalación."
        Write-Fail "Intentá cerrar y reabrir la terminal, luego ejecutá 'rai --version'."
        exit 1
    }
}

# ─────────────────────────────────────────────
# STEP 6: Claude Code CLI
# ─────────────────────────────────────────────

if (-not $SkipClaudeCode) {
    Write-Step "Instalando Claude Code CLI"

    if (Test-Command "claude") {
        Write-Ok "Claude Code ya instalado: $(claude --version 2>$null)"
    } elseif (Test-Command "npm") {
        Write-Host "  Instalando Claude Code via npm..." -ForegroundColor Gray
        npm install -g @anthropic-ai/claude-code
        Refresh-Path

        if (Test-Command "claude") {
            Write-Ok "Claude Code instalado: $(claude --version 2>$null)"
        } else {
            Write-Warn "Claude Code no encontrado en PATH. Intentá reiniciar la terminal."
        }
    } else {
        Write-Warn "npm no disponible. Instalá Claude Code manualmente:"
        Write-Warn "  https://claude.ai/claude-code"
    }
}

# ─────────────────────────────────────────────
# STEP 7: Variables de ambiente
# ─────────────────────────────────────────────

Write-Step "Configurando variables de ambiente"

$envScope = [System.EnvironmentVariableTarget]::User

# Auth — Claude Code
if ($ApiKey) {
    [System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $ApiKey, $envScope)
    $env:ANTHROPIC_API_KEY = $ApiKey
    Write-Ok "ANTHROPIC_API_KEY configurada"
} elseif ($ClaudeToken) {
    [System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_TOKEN", $ClaudeToken, $envScope)
    $env:CLAUDE_CODE_TOKEN = $ClaudeToken
    Write-Ok "CLAUDE_CODE_TOKEN configurada"
} else {
    Write-Warn "No se proporcionó clave de autenticación."
    Write-Warn "Configurá una de estas variables manualmente:"
    Write-Warn "  ANTHROPIC_API_KEY=sk-ant-...   (API key — pago por uso)"
    Write-Warn "  CLAUDE_CODE_TOKEN=cct_...      (token de suscripción Pro/Max)"
    Write-Host ""
    Write-Host "  Podés setear variables de ambiente así:" -ForegroundColor Gray
    Write-Host '  [System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")' -ForegroundColor Gray
}

# Verificar si ya hay auth en el ambiente (caso: segunda ejecución)
$existingApiKey = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", $envScope)
$existingToken  = [System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_TOKEN", $envScope)

if ($existingApiKey) {
    Write-Ok "ANTHROPIC_API_KEY ya configurada en el ambiente de usuario"
} elseif ($existingToken) {
    Write-Ok "CLAUDE_CODE_TOKEN ya configurada en el ambiente de usuario"
}

# ─────────────────────────────────────────────
# STEP 8: Verificación final
# ─────────────────────────────────────────────

Write-Step "Verificación final"

$allOk = $true

# Python
if (Test-Command "python") {
    $v = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    Write-Ok "python $v"
} else {
    Write-Fail "python no encontrado"
    $allOk = $false
}

# pipx
if (Test-Command "pipx") {
    Write-Ok "pipx $(pipx --version)"
} else {
    Write-Fail "pipx no encontrado"
    $allOk = $false
}

# rai
if (Test-Command "rai") {
    Write-Ok "rai $(rai --version 2>$null)"
} else {
    Write-Fail "rai no encontrado"
    $allOk = $false
}

# claude
if (-not $SkipClaudeCode) {
    if (Test-Command "claude") {
        Write-Ok "claude $(claude --version 2>$null)"
    } else {
        Write-Warn "claude no encontrado (requerido para RaiSE)"
    }
}

# ─────────────────────────────────────────────
# STEP 9: Próximos pasos
# ─────────────────────────────────────────────

Write-Host ""
if ($allOk) {
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  Instalación completada." -ForegroundColor Green
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
} else {
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Instalación parcial — revisá los errores." -ForegroundColor Yellow
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Yellow
}

Write-Host @"

PRÓXIMOS PASOS:

  1. Reiniciá la terminal (para que el PATH tome efecto)

  2. Autenticá Claude Code (si no pasaste -ApiKey/-ClaudeToken):
       claude setup-token       # Suscripción Pro/Max (recomendado)
     o bien:
       Setear ANTHROPIC_API_KEY en variables de ambiente

  3. Inicializá RaiSE en tu proyecto:
       cd C:\ruta\a\tu\proyecto
       rai init

  4. Configurá tu perfil de desarrollador (primera vez):
       rai session start --name "Tu Nombre"

  5. Verificá el estado de la instalación:
       rai doctor

REFERENCIAS:
  Docs RaiSE:    https://raiseframework.ai/docs
  Claude Code:   https://claude.ai/claude-code
  Soporte:       https://github.com/humansys-ai/raise-commons/issues

"@ -ForegroundColor White
