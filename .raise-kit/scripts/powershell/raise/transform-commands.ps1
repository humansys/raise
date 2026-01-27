# transform-commands.ps1
param (
    [string]$ProjectName = "speckit"
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptPath = $MyInvocation.MyCommand.Path
$ScriptDir = Split-Path $ScriptPath
# Script is in .raise-kit/scripts/powershell/raise
# RepoRoot is 4 levels up: .raise-kit/scripts/powershell/raise -> ../../../..
$RepoRoot = Resolve-Path "$ScriptDir/../../../.."
$RepoRootPath = $RepoRoot.Path

$ProjectDir = Join-Path $RepoRootPath $ProjectName
$SrcDir = Join-Path $ProjectDir ".claude/commands"
$DestDir = Join-Path $ProjectDir ".claude/commands"
$BaseRaiseKit = Join-Path $RepoRootPath ".raise-kit"

Write-Host "Transform Commands Script v1.0.0 (PowerShell)"
Write-Host "========================================"
Write-Host "Project: $ProjectName"
# Write-Host "Repo Root: $RepoRootPath"

# File Mapping
$FileMap = @{
    "speckit.specify.md" = "03-feature/speckit.1.specify.md"
    "speckit.clarify.md" = "03-feature/speckit.2.clarify.md"
    "speckit.plan.md" = "03-feature/speckit.3.plan.md"
    "speckit.tasks.md" = "03-feature/speckit.4.tasks.md"
    "speckit.analyze.md" = "03-feature/speckit.5.analyze.md"
    "speckit.implement.md" = "03-feature/speckit.6.implement.md"
    "speckit.checklist.md" = "03-feature/speckit.util.checklist.md"
    "speckit.taskstoissues.md" = "03-feature/speckit.util.issues.md"
    "speckit.constitution.md" = "01-onboarding/speckit.2.constitution.md"
}

# Reference Mapping
$RefMap = @{
    "speckit.specify" = "speckit.1.specify"
    "speckit.clarify" = "speckit.2.clarify"
    "speckit.plan" = "speckit.3.plan"
    "speckit.tasks" = "speckit.4.tasks"
    "speckit.analyze" = "speckit.5.analyze"
    "speckit.implement" = "speckit.6.implement"
    "speckit.checklist" = "speckit.util.checklist"
    "speckit.taskstoissues" = "speckit.util.issues"
    "speckit.constitution" = "speckit.2.constitution"
}

# Stats
$SuccessCount = 0
$ErrorCount = 0

function Copy-BaseAssets {
    # 1. Copy base commands from .raise-kit/commands to .claude/commands
    $CmdSrc = Join-Path $BaseRaiseKit "commands"
    $CmdTarget = Join-Path $ProjectDir ".claude/commands"
    
    if (Test-Path $CmdSrc) {
        Write-Host "  Copying commands base..."
        if (-not (Test-Path $CmdTarget)) {
             New-Item -ItemType Directory -Force -Path $CmdTarget | Out-Null
        }
        Copy-Item -Path "$CmdSrc/*" -Destination $CmdTarget -Recurse -Force
    }

    # 2. Copy gates and templates to .specify
    $AssetsToCopy = @("gates", "templates")
    foreach ($Dir in $AssetsToCopy) {
        $Src = Join-Path $BaseRaiseKit $Dir
        $Target = Join-Path $ProjectDir ".specify/$Dir"
        if (Test-Path $Src) {
            Write-Host "  Copying $Dir..."
            if (-not (Test-Path $Target)) {
                New-Item -ItemType Directory -Force -Path $Target | Out-Null
            }
            Copy-Item -Path "$Src/*" -Destination $Target -Recurse -Force
        }
    }

    # 3. Handle scripts specifically: Copy only powershell (and common files if any), exclude bash
    $ScriptsSrc = Join-Path $BaseRaiseKit "scripts"
    $ScriptsTarget = Join-Path $ProjectDir ".specify/scripts"
    
    if (Test-Path $ScriptsSrc) {
        Write-Host "  Copying scripts (PowerShell only)..."
        if (-not (Test-Path $ScriptsTarget)) {
            New-Item -ItemType Directory -Force -Path $ScriptsTarget | Out-Null
        }
        
        # Copy powershell folder
        $PsSrc = Join-Path $ScriptsSrc "powershell"
        if (Test-Path $PsSrc) {
             $PsTarget = Join-Path $ScriptsTarget "powershell"
             if (-not (Test-Path $PsTarget)) { New-Item -ItemType Directory -Force -Path $PsTarget | Out-Null }
             Copy-Item -Path "$PsSrc/*" -Destination $PsTarget -Recurse -Force
        }
        
        # Copy direct files in scripts (e.g. common stuff) but skip bash folder
        Get-ChildItem -Path $ScriptsSrc -File | ForEach-Object {
            Copy-Item -Path $_.FullName -Destination $ScriptsTarget -Force
        }
    }
    Write-Host ""
}

function Transform-File {
    param ($SrcFile, $DestRelPath)
    
    $SrcFullPath = Join-Path $SrcDir $SrcFile
    $DestFullPath = Join-Path $DestDir $DestRelPath

    if (-not (Test-Path $SrcFullPath)) {
        Write-Warning "Source file not found: $SrcFile"
        $global:ErrorCount++
        return
    }

    # Ensure dest dir exists
    $DestFileDir = Split-Path $DestFullPath
    if (-not (Test-Path $DestFileDir)) {
        New-Item -ItemType Directory -Force -Path $DestFileDir | Out-Null
    }

    # Read content
    $Content = Get-Content -Path $SrcFullPath -Raw -Encoding UTF8

    # Replace refs
    foreach ($OldRef in $RefMap.Keys) {
        $NewRef = $RefMap[$OldRef]
        $Content = $Content.Replace($OldRef, $NewRef)
    }

    # Write content
    Set-Content -Path $DestFullPath -Value $Content -Encoding UTF8
    
    # Remove source file
    Remove-Item -Path $SrcFullPath -Force
    
    Write-Host "  Moved: $SrcFile -> $DestRelPath"
    $global:SuccessCount++
}

function Run-Transformation {
    Write-Host "Starting transformation..."
    
    # Create main dest dirs
    if (-not (Test-Path $DestDir)) {
        New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
    }

    foreach ($SrcFile in $FileMap.Keys) {
        Transform-File -SrcFile $SrcFile -DestRelPath $FileMap[$SrcFile]
    }
}

# Main Execution
try {
    Copy-BaseAssets
    if (Test-Path $SrcDir) {
        Run-Transformation
    } else {
        Write-Warning "Source directory not found: $SrcDir (skipping transformation, only assets copied)"
    }

    Write-Host "========================================"
    Write-Host "Summary"
    Write-Host "Successful: $SuccessCount"
    Write-Host "Failed: $ErrorCount"

    if ($ErrorCount -eq 0) {
        Write-Host "SUCCESS"
    } else {
        Write-Host "WARNING: Completed with errors"
        exit 1
    }
} catch {
    Write-Error $_
    exit 1
}
