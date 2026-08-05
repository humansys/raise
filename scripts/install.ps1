#!/usr/bin/env pwsh
# scripts/install.ps1 — Install rai + rai-mcp-pipeline standalone binaries (Windows)
#
# No Python required — downloads prebuilt onedir binaries and installs them
# atomically: if either binary fails to download or verify, nothing is
# installed or modified (rai and rai-mcp-pipeline never end up at different
# versions).
#
# Usage:
#   irm https://github.com/humansys/raise/releases/latest/download/install.ps1 | iex
#   ./install.ps1                                # installs latest release
#   ./install.ps1 -Version v3.1.0
#   ./install.ps1 -Version v3.1.0 -Prefix C:\rai
#   $env:BASE_URL = "https://example.com"; ./install.ps1 -Version v3.1.0
#
# Env overrides: RAI_VERSION, BASE_URL (same as -Version/-BaseUrl)

param(
    [string]$Version = $env:RAI_VERSION,
    [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else {
        # Default: GitHub Releases in humansys/raise (RAISE-15664) — the
        # build.yml workflow publishes each binary + .sha256 as a Release asset.
        "https://github.com/humansys/raise/releases/download"
    }),
    [string]$Prefix = (Join-Path ([System.Environment]::GetFolderPath('LocalApplicationData')) 'rai')
)

$ErrorActionPreference = 'Stop'
$Binaries = @('rai', 'rai-mcp-pipeline')
$Platform = 'windows-x86_64'

function Step($msg) { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Ok($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

function Add-ToUserPath {
    param([string]$Dir)
    # Registers $Dir in the user's persistent PATH (HKCU\Environment on real
    # Windows — GetEnvironmentVariable/SetEnvironmentVariable with the "User"
    # scope is a no-op on non-Windows platforms, which is why this path is
    # verified separately from the download/checksum/install logic). Also
    # updates the current process's $env:Path so rai/rai-mcp-pipeline work
    # immediately in the running session, without waiting for a new terminal.
    $currentUserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($currentUserPath -notlike "*$Dir*") {
        $newUserPath = if ([string]::IsNullOrEmpty($currentUserPath)) { $Dir } else { "$currentUserPath;$Dir" }
        [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
    }
    if ($env:Path -notlike "*$Dir*") {
        $env:Path = "$env:Path;$Dir"
    }
    Ok "PATH updated: $Dir"
}

function Remove-LegacyShim {
    # Pre-binary installs (docs/install.ps1) left a rai.cmd shim here that
    # resolves to .venv\Scripts\rai.exe in the current directory. Left in
    # place, it shadows the binaries this script installs (RAISE-15801).
    param([string]$Path = (Join-Path $env:USERPROFILE '.local\bin\rai.cmd'))
    if (Test-Path $Path) {
        Remove-Item $Path -Force
        Ok "Legacy shim removed: $Path"
    }
}

# Guarded so this script can be dot-sourced (Pester) to unit-test the
# functions above without triggering real downloads/installs.
if ($MyInvocation.InvocationName -ne '.') {

Step 'Checking for legacy install artifacts'
Remove-LegacyShim

if (-not $Version) {
    Step 'No version specified — resolving latest release from GitHub'
    try {
        $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/humansys/raise/releases/latest' -UseBasicParsing
        $Version = $release.tag_name
    } catch {
        Fail 'Could not resolve latest version. Pass -Version vX.Y.Z or set RAI_VERSION.'
        exit 1
    }
    if (-not $Version) {
        Fail 'Could not resolve latest version. Pass -Version vX.Y.Z or set RAI_VERSION.'
        exit 1
    }
    Ok "Latest version: $Version"
}

Step "Installing rai + rai-mcp-pipeline $Version for $Platform"

$TmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('rai-install-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null

try {
    # Phase 1: download + verify ALL binaries before installing ANY of them.
    # This is what makes the install atomic — a failure here never reaches
    # the filesystem mutation phase below, so rai and rai-mcp-pipeline can
    # never end up at different versions.
    foreach ($name in $Binaries) {
        $archive = "$name-$Platform.zip"
        $url = "$BaseUrl/$Version/$archive"
        $dest = Join-Path $TmpRoot $archive

        Step "Downloading $name ($archive)"
        try {
            Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        } catch {
            Fail "Download failed: $url"
            Fail 'Aborting - nothing was installed or modified.'
            exit 1
        }

        $shaDest = "$dest.sha256"
        try {
            Invoke-WebRequest -Uri "$url.sha256" -OutFile $shaDest -UseBasicParsing
        } catch {
            Fail "Checksum download failed: $url.sha256"
            Fail 'Aborting - nothing was installed or modified.'
            exit 1
        }

        Step "Verifying checksum for $name"
        $expected = (Get-Content $shaDest -Raw).Trim().Split(' ')[0].ToLower()
        $actual = (Get-FileHash -Path $dest -Algorithm SHA256).Hash.ToLower()
        if ($expected -ne $actual) {
            Fail "Checksum verification failed for $archive"
            Fail 'Aborting - nothing was installed or modified.'
            exit 1
        }
        Ok "$name verified"
    }

    # Phase 2: extract + install. Only reached once every binary above has
    # downloaded and verified successfully.
    New-Item -ItemType Directory -Path $Prefix -Force | Out-Null

    foreach ($name in $Binaries) {
        $archive = Join-Path $TmpRoot "$name-$Platform.zip"
        $targetDir = Join-Path $Prefix $name
        $staging = Join-Path $TmpRoot "staging-$name"

        New-Item -ItemType Directory -Path $staging -Force | Out-Null
        Expand-Archive -Path $archive -DestinationPath $staging -Force

        # Atomic swap: rename is atomic within the same volume, so an
        # install never leaves $targetDir half-written. Rename-Item only
        # renames within the same parent directory (it errors given a full
        # path), so the cross-directory staging -> targetDir move uses
        # Move-Item instead.
        if (Test-Path "$targetDir.old") { Remove-Item "$targetDir.old" -Recurse -Force }
        if (Test-Path $targetDir) { Rename-Item -Path $targetDir -NewName "$(Split-Path $targetDir -Leaf).old" }
        Move-Item -Path $staging -Destination $targetDir
        if (Test-Path "$targetDir.old") { Remove-Item "$targetDir.old" -Recurse -Force }

        Add-ToUserPath -Dir $targetDir
        Ok "$name installed to $targetDir"
    }

    Step 'Done'
    Ok "rai + rai-mcp-pipeline $Version installed"
} finally {
    Remove-Item $TmpRoot -Recurse -Force -ErrorAction SilentlyContinue
}

}
