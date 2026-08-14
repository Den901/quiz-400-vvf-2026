param([string]$ProjectDir = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$CloudDir = Join-Path $ProjectDir 'cloud'
$BackupDir = Join-Path $CloudDir 'backups'
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$container = (& docker compose --env-file (Join-Path $CloudDir '.env') -f (Join-Path $CloudDir 'compose.yml') ps -q database).Trim()
if (-not $container) { throw 'Container PostgreSQL non disponibile.' }
$inside = "/tmp/quiz400-$stamp.dump"
& docker exec $container pg_dump -U quiz400 -d quiz400 -Fc --file=$inside
if ($LASTEXITCODE -ne 0) { throw 'Backup PostgreSQL non riuscito.' }
$destination = Join-Path $BackupDir "quiz400-$stamp.dump"
& docker cp "${container}:$inside" $destination
if ($LASTEXITCODE -ne 0) { throw 'Copia del backup PostgreSQL non riuscita.' }
& docker exec $container rm -f $inside
Get-ChildItem -LiteralPath $BackupDir -Filter 'quiz400-*.dump' -File | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item -Force
Write-Host "Backup creato: $destination"
