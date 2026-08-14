$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$CloudDir = Join-Path $ProjectDir 'cloud'
$EnvFile = Join-Path $CloudDir '.env'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop non è installato. Installalo, avvialo e rilancia questo script come amministratore.'
}
& docker compose version | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose non è disponibile.' }

function New-HexSecret([int]$Bytes) {
    $buffer = New-Object byte[] $Bytes
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($buffer) } finally { $generator.Dispose() }
    return -join ($buffer | ForEach-Object { $_.ToString('x2') })
}

function Test-Port([int]$Port) {
    return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    $username = Read-Host 'Nome utente amministratore [admin]'
    if (-not $username) { $username = 'admin' }
    if ($username -notmatch '^[A-Za-z0-9._-]{3,40}$') { throw 'Il nome utente deve avere 3-40 caratteri: lettere, numeri, punto, trattino o trattino basso.' }
    $name = Read-Host 'Nome visualizzato [Amministratore]'
    if (-not $name) { $name = 'Amministratore' }
    $email = Read-Host 'Email amministratore (facoltativa)'
    $securePassword = Read-Host 'Password amministratore (almeno 10 caratteri)' -AsSecureString
    $password = [Net.NetworkCredential]::new('', $securePassword).Password
    if ($password.Length -lt 10) { throw 'La password deve avere almeno 10 caratteri.' }
    if ($password -notmatch '^[A-Za-z0-9._!@%+=,:/-]+$') { throw 'Per il file di configurazione usa lettere, numeri e i simboli . _ ! @ % + = , : / -' }
    $port = 8088
    while (Test-Port $port) { $port++ }
    $lines = @(
        "POSTGRES_PASSWORD=$(New-HexSecret 32)",
        "APP_SECRET=$(New-HexSecret 48)",
        "ADMIN_USERNAME=$username",
        "ADMIN_NAME=$name",
        "ADMIN_EMAIL=$email",
        "ADMIN_PASSWORD=$password",
        'HTTP_PORT=80',
        'HTTPS_PORT=443',
        "APP_PORT=$port",
        'APP_BIND_ADDRESS=0.0.0.0',
        'PROXY_MODE=external',
        'COMPOSE_PROFILES=',
        'PORT_CONTROL_CONTAINER_DIR=/srv/quiz400-control'
    )
    [IO.File]::WriteAllLines($EnvFile, $lines, [Text.UTF8Encoding]::new($false))
    Write-Host "Configurazione creata. Backend disponibile sulla porta $port."
}

New-Item -ItemType Directory -Force -Path (Join-Path $CloudDir 'control\uploads'), (Join-Path $CloudDir 'backups') | Out-Null
& docker compose --env-file $EnvFile -f (Join-Path $CloudDir 'compose.yml') up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Avvio iniziale non riuscito.' }

$watcher = Join-Path $CloudDir 'server-control-windows.ps1'
$argument = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$watcher`" -ProjectDir `"$ProjectDir`""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName 'Quiz400VVF-ServerControl' -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName 'Quiz400VVF-ServerControl'
Write-Host 'Portale Windows installato. Aggiornamenti, riavvio e spegnimento dal pannello Admin sono attivi.'
