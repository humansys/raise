#!/usr/bin/env pwsh
# scripts/install.ps1 — Install rai + rai-mcp-pipeline standalone binaries (Windows)
#
# No Python required — downloads prebuilt onedir binaries and installs them
# atomically: if either binary fails to download or verify, nothing is
# installed or modified (rai and rai-mcp-pipeline never end up at different
# versions).
#
# Usage:
#   irm https://releases.raiseframework.ai/install.ps1 | iex
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
        "https://releases.raiseframework.ai"
    }),
    [string]$Prefix = (Join-Path ([System.Environment]::GetFolderPath('LocalApplicationData')) 'rai')
)

$ErrorActionPreference = 'Stop'
$Binaries = @('rai', 'rai-mcp-pipeline')
$Platform = 'windows-x86_64'

function Step($msg) { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Ok($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

function Update-PathValue {
    # Pure function: returns $Dir prepended to $PathValue, with any pre-existing
    # segments that exactly equal $Dir (case-insensitive, trailing-backslash
    # insensitive) removed first. Never touches segments the installer does not
    # manage (design D2 — exact-match-only, no general PATH cleanup).
    param(
        [string]$PathValue,
        [string]$Dir
    )
    $normalDir = $Dir.TrimEnd('\')
    $segments = if ([string]::IsNullOrEmpty($PathValue)) {
        @()
    } else {
        $PathValue -split ';' | Where-Object {
            $_.TrimEnd('\') -ne $normalDir  # case-insensitive on Windows FS; -ne is case-insensitive in pwsh by default
        }
    }
    # Prepend $Dir (canonical form, no trailing backslash added — keep caller's form)
    $result = @($Dir) + $segments
    return ($result -join ';')
}

function Add-ToUserPath {
    param([string]$Dir)
    # Registers $Dir in the user's persistent PATH (HKCU\Environment on real
    # Windows — GetEnvironmentVariable/SetEnvironmentVariable with the "User"
    # scope is a no-op on non-Windows platforms, which is why this path is
    # verified separately from the download/checksum/install logic). Also
    # updates the current process's $env:Path so rai/rai-mcp-pipeline work
    # immediately in the running session, without waiting for a new terminal.
    $currentUserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $newUserPath = Update-PathValue -PathValue $currentUserPath -Dir $Dir
    [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
    $env:Path = Update-PathValue -PathValue $env:Path -Dir $Dir
    Ok "PATH updated: $Dir"
}

function Unblock-Download {
    # Removes the NTFS Zone.Identifier mark-of-the-web (MotW) that
    # Invoke-WebRequest stamps on downloaded files, so Expand-Archive does
    # not propagate it to every extracted file (RAISE-17099 T5, D5) — the
    # mechanism behind Windows SmartScreen blocking an unsigned rai.exe or
    # the installer on first Explorer launch. Called only after checksum
    # verification succeeds: integrity is checked before trust is granted.
    # -ErrorAction SilentlyContinue: Unblock-File on a non-NTFS volume, or a
    # file with no zone stream, is a no-op rather than a hard failure — this
    # is defense in depth, not a step the install can safely abort on.
    param([string]$Path)
    Unblock-File -Path $Path -ErrorAction SilentlyContinue
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

        # Checksum passed — integrity is established, so it is now safe to
        # remove the mark-of-the-web before extraction (D5).
        Unblock-Download -Path $dest
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
    Write-Host ""
    Write-Host "Next step - enter your repository and run:"
    Write-Host "  cd C:\path\to\your\project"
    Write-Host "  rai onboard"
    Write-Host ""
    Write-Host 'If Windows SmartScreen blocks rai.exe or the installer: choose "More info" -> "Run anyway", or run: Unblock-File <path>'
} finally {
    Remove-Item $TmpRoot -Recurse -Force -ErrorAction SilentlyContinue
}

}
