# scripts/install.Tests.ps1 — Pester tests for legacy shim cleanup (RAISE-15801)
#
# Dot-sources install.ps1 to exercise Remove-LegacyShim in isolation. The
# script's main body (download/verify/install) is guarded behind
# `if ($MyInvocation.InvocationName -ne '.')` so dot-sourcing here only
# defines functions — no network calls happen during these tests.

BeforeAll {
    . "$PSScriptRoot/install.ps1"
}

Describe 'Update-PathValue' {
    # Pure function — no registry/env side-effects in tests.
    # Four cases from design E3, plus case-insensitivity and trailing-backslash.

    It 'promotes existing exact entry to front' {
        $result = Update-PathValue -PathValue 'C:\old;C:\rai acceptance\prefix with spaces\rai;C:\other' `
                                   -Dir 'C:\rai acceptance\prefix with spaces\rai'
        $result | Should -Be 'C:\rai acceptance\prefix with spaces\rai;C:\old;C:\other'
    }

    It 'prepends when dir is absent' {
        $result = Update-PathValue -PathValue 'C:\old;C:\other' -Dir 'C:\new dir\rai'
        $result | Should -Be 'C:\new dir\rai;C:\old;C:\other'
    }

    It 'handles empty PATH' {
        $result = Update-PathValue -PathValue '' -Dir 'C:\new dir\rai'
        $result | Should -Be 'C:\new dir\rai'
    }

    It 'does not touch near-miss C:\rai-old when managing C:\rai' {
        $result = Update-PathValue -PathValue 'C:\rai-old;C:\x' -Dir 'C:\rai'
        $result | Should -Be 'C:\rai;C:\rai-old;C:\x'
    }

    It 'is case-insensitive when removing exact match' {
        $result = Update-PathValue -PathValue 'C:\Rai Acceptance\Prefix;C:\other' `
                                   -Dir 'C:\rai acceptance\prefix'
        $result | Should -Be 'C:\rai acceptance\prefix;C:\other'
    }

    It 'ignores trailing backslash difference when deduplicating' {
        $result = Update-PathValue -PathValue 'C:\rai\;C:\other' -Dir 'C:\rai'
        $result | Should -Be 'C:\rai;C:\other'
    }
}

Describe 'Unblock-Download' {
    # NTFS alternate-data-stream (Zone.Identifier) only exists on real
    # Windows filesystems, so these are Windows-only (RAISE-17099 T5, D5).
    BeforeEach {
        $TestRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('rai-unblock-test-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $TestRoot -Force | Out-Null
        $DownloadPath = Join-Path $TestRoot 'rai-windows-x86_64.zip'
        Set-Content -Path $DownloadPath -Value 'not a real zip, just bytes'
    }

    AfterEach {
        Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    It 'removes the Zone.Identifier mark-of-the-web stream' -Skip:(-not $IsWindows) {
        Set-Content -Path $DownloadPath -Stream Zone.Identifier -Value "[ZoneTransfer]`nZoneId=3"
        (Get-Item -Path $DownloadPath -Stream Zone.Identifier -ErrorAction SilentlyContinue) | Should -Not -BeNullOrEmpty

        Unblock-Download -Path $DownloadPath

        (Get-Item -Path $DownloadPath -Stream Zone.Identifier -ErrorAction SilentlyContinue) | Should -BeNullOrEmpty
    }

    It 'does not throw and leaves an unmarked file untouched' -Skip:(-not $IsWindows) {
        { Unblock-Download -Path $DownloadPath } | Should -Not -Throw

        Test-Path $DownloadPath | Should -BeTrue
        (Get-Content -Path $DownloadPath -Raw) | Should -Be "not a real zip, just bytes`n"
    }
}

Describe 'Remove-LegacyShim' {
    BeforeEach {
        $TestRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('rai-shim-test-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $TestRoot -Force | Out-Null
        $ShimPath = Join-Path $TestRoot 'rai.cmd'
    }

    AfterEach {
        Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    It 'removes the legacy shim when present' {
        Set-Content -Path $ShimPath -Value '@echo off'
        Test-Path $ShimPath | Should -BeTrue

        Remove-LegacyShim -Path $ShimPath

        Test-Path $ShimPath | Should -BeFalse
    }

    It 'does nothing when no legacy shim is present' {
        Test-Path $ShimPath | Should -BeFalse

        { Remove-LegacyShim -Path $ShimPath } | Should -Not -Throw

        Test-Path $ShimPath | Should -BeFalse
    }

    It 'does not touch unrelated files in the same directory' {
        $OtherFile = Join-Path $TestRoot 'other.txt'
        Set-Content -Path $OtherFile -Value 'keep me'
        Set-Content -Path $ShimPath -Value '@echo off'

        Remove-LegacyShim -Path $ShimPath

        Test-Path $OtherFile | Should -BeTrue
    }
}
