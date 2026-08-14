param([string]$ProjectDir = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
& docker compose --env-file (Join-Path $ProjectDir 'cloud\.env') -f (Join-Path $ProjectDir 'cloud\compose.yml') up -d --no-build app
if ($LASTEXITCODE -ne 0) { throw 'Avvio del portale non riuscito.' }
Write-Host 'Portale avviato.'
