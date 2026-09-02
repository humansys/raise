# scripts/build-binary-local.ps1 — RAISE-15630
#
# PowerShell mirror of build-binary-local.sh (RAISE-15629) for the Windows
# SaaS runner, where PowerShell is the native shell, not bash. Same repeatable
# build + smoke test for the two PyInstaller onedir binaries (rai,
# rai-mcp-pipeline).
$ErrorActionPreference = "Stop"

$RepoRoot = (git rev-parse --show-toplevel)
$CliDir = Join-Path $RepoRoot "packages/raise-cli"

Write-Host "==> Building rai (raise-cli.spec)"
Push-Location $CliDir
try {
    uv run pyinstaller --noconfirm raise-cli.spec
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "==> Building rai-mcp-pipeline (raise-mcp-pipeline.spec)"
    uv run pyinstaller --noconfirm raise-mcp-pipeline.spec
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}

$RaiBin = Join-Path $CliDir "dist/rai/rai.exe"
$McpBin = Join-Path $CliDir "dist/rai-mcp-pipeline/rai-mcp-pipeline.exe"

Write-Host "==> Smoke test: rai gate list (expect 48)"
$gateJson = & $RaiBin gate list --format json | ConvertFrom-Json
$gateCount = $gateJson.gates.Count
Write-Host "    gates found: $gateCount"
if ($gateCount -ne 48) {
    Write-Error "FAIL: expected 48 gates, got $gateCount — .spec is missing metadata/submodules for an entry-point group"
    exit 1
}

Write-Host "==> Smoke test: rai adapter list"
& $RaiBin adapter list

Write-Host "==> Smoke test: rai-mcp-pipeline exposes MCP tools over stdio"
# Same rationale as the bash version: a bare process-liveness check is
# unreliable here — with no real MCP client attached, the stdio transport
# sees EOF on stdin and exits by design. McpBridge does a real handshake and
# gives an actual tool count instead of inferring from logs.
$toolCountScript = @'
import asyncio
import sys

from raise_cli.mcp.bridge import McpBridge


async def main() -> int:
    bridge = McpBridge(server_command=sys.argv[1])
    tools = await bridge.list_tools()
    await bridge.aclose()
    print(len(tools))
    return 0


sys.exit(asyncio.run(main()))
'@

$toolCount = $toolCountScript | uv run python - $McpBin
Write-Host "    tools found: $toolCount"
if ([int]$toolCount -lt 30) {
    Write-Error "FAIL: expected ~36 MCP tools, got $toolCount"
    exit 1
}

Write-Host "==> All smoke tests passed"
