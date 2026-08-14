param([Parameter(Mandatory = $true)][string]$ProjectDir)
$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
if ($ProjectDir -eq [IO.Path]::GetPathRoot($ProjectDir)) { throw 'Percorso progetto non consentito.' }
$CloudDir = Join-Path $ProjectDir 'cloud'
$ControlDir = Join-Path $CloudDir 'control'
$RequestFile = Join-Path $ControlDir 'server-request.json'
$ProcessingFile = Join-Path $ControlDir 'server-request.processing.json'
$StatusFile = Join-Path $ControlDir 'server-status.json'
$EnvFile = Join-Path $CloudDir '.env'
$ComposeFile = Join-Path $CloudDir 'compose.yml'
New-Item -ItemType Directory -Force -Path (Join-Path $ControlDir 'uploads') | Out-Null

function Write-PortalStatus([string]$State, [string]$Message = '', [string]$RequestId = '', [string]$Version = '') {
    $payload = [ordered]@{ state = $State; at = [DateTime]::UtcNow.ToString('o') }
    if ($Message) { $payload.message = $Message }
    if ($RequestId) { $payload.requestId = $RequestId }
    if ($Version) { $payload.version = $Version }
    $temporary = "$StatusFile.tmp"
    [IO.File]::WriteAllText($temporary, ($payload | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $StatusFile -Force
}

function Invoke-Compose([string[]]$Arguments) {
    & docker compose --env-file $EnvFile -f $ComposeFile @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose non riuscito: $($Arguments -join ' ')" }
}

function Read-EnvValue([string]$Name, [string]$Default) {
    $line = Get-Content -LiteralPath $EnvFile | Where-Object { $_ -match "^$([Regex]::Escape($Name))=" } | Select-Object -Last 1
    if ($line) { return ($line -split '=', 2)[1] }
    return $Default
}

function Wait-PortalHealthy {
    $port = Read-EnvValue 'APP_PORT' '8088'
    for ($attempt = 0; $attempt -lt 120; $attempt++) {
        try {
            $result = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri "http://127.0.0.1:$port/api/health"
            if ($result.StatusCode -eq 200) { return }
        } catch {}
        Start-Sleep -Seconds 2
    }
    throw 'Il portale non è tornato disponibile.'
}

while ($true) {
    if (-not (Test-Path -LiteralPath $RequestFile)) { Start-Sleep -Seconds 2; continue }
    try {
        Move-Item -LiteralPath $RequestFile -Destination $ProcessingFile -Force
        $request = Get-Content -LiteralPath $ProcessingFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($request.action -notin @('update', 'restart', 'stop') -or $request.requestId -notmatch '^[0-9a-f-]{36}$') { throw 'Richiesta non valida.' }
        if ($request.action -eq 'restart') {
            Write-PortalStatus 'restarting' 'Riavvio del portale in corso.' $request.requestId
            Invoke-Compose @('up', '-d', '--no-build', '--force-recreate', 'app')
            Wait-PortalHealthy
            Write-PortalStatus 'completed' 'Portale riavviato correttamente.' $request.requestId
            continue
        }
        if ($request.action -eq 'stop') {
            Write-PortalStatus 'stopping' 'Arresto del solo portale in corso; Windows resta acceso.' $request.requestId
            Invoke-Compose @('stop', 'app')
            Write-PortalStatus 'stopped' 'Portale arrestato. Usa cloud\start-windows.ps1 per riaccenderlo.' $request.requestId
            continue
        }
        if ($request.targetVersion -notmatch '^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$') { throw 'Versione non valida.' }
        $workDir = Join-Path $ControlDir ("server-update-" + [Guid]::NewGuid())
        $stageDir = Join-Path $workDir 'stage'
        $package = Join-Path $workDir 'update.zip'
        New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
        Write-PortalStatus 'downloading' "Preparazione del pacchetto $($request.targetVersion)." $request.requestId $request.targetVersion
        if ($request.source -eq 'github') {
            if ($request.assetUrl -notmatch '^https://github\.com/Den901/quiz-400-vvf-2026/releases/download/') { throw 'URL release non consentito.' }
            Invoke-WebRequest -UseBasicParsing -Uri $request.assetUrl -OutFile $package
        } elseif ($request.source -eq 'upload' -and $request.filePath -match '^uploads/update-[0-9a-f-]{36}\.zip$') {
            $uploaded = (Resolve-Path -LiteralPath (Join-Path $ControlDir $request.filePath)).Path
            if (-not $uploaded.StartsWith((Join-Path $ControlDir 'uploads'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Percorso upload non consentito.' }
            Copy-Item -LiteralPath $uploaded -Destination $package
        } else { throw 'Origine aggiornamento non valida.' }
        if ($request.sha256) {
            $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $package).Hash.ToLowerInvariant()
            if ($actual -ne $request.sha256) { throw 'Controllo di integrità del pacchetto non riuscito.' }
        }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $archive = [IO.Compression.ZipFile]::OpenRead($package)
        try {
            foreach ($entry in $archive.Entries) {
                $candidate = [IO.Path]::GetFullPath((Join-Path $stageDir $entry.FullName))
                if (-not $candidate.StartsWith($stageDir + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Percorso non sicuro nel pacchetto.' }
            }
        } finally { $archive.Dispose() }
        [IO.Compression.ZipFile]::ExtractToDirectory($package, $stageDir)
        $manifest = Get-Content -LiteralPath (Join-Path $stageDir 'release-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        $versionFile = Get-Content -LiteralPath (Join-Path $stageDir 'version.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($manifest.app -ne 'Quiz 400 VVF 2026 Server' -or $manifest.version -ne $request.targetVersion -or $versionFile.version -ne $request.targetVersion) { throw 'Manifest o versione non corrispondente.' }
        foreach ($item in $manifest.files) {
            if ($item.path -match '(^/|^\\|\.\.)') { throw 'Percorso manifest non sicuro.' }
            $source = Join-Path $stageDir $item.path
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "File mancante: $($item.path)" }
            if ((Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Hash non valido: $($item.path)" }
        }
        Write-PortalStatus 'backing-up' 'Backup PostgreSQL e copia dei file correnti.' $request.requestId $request.targetVersion
        & (Join-Path $CloudDir 'backup-windows.ps1') -ProjectDir $ProjectDir
        if ($LASTEXITCODE -ne 0) { throw 'Backup PostgreSQL non riuscito.' }
        $sourceBackup = Join-Path (Join-Path $CloudDir 'backups') ("source-before-$($request.targetVersion)-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.tar.gz')
        & tar.exe -czf $sourceBackup --exclude=.git --exclude=cloud/.env --exclude=cloud/backups --exclude=cloud/control --exclude=cloud/data --exclude=tmp -C $ProjectDir .
        if ($LASTEXITCODE -ne 0) { throw 'Copia dei file correnti non riuscita.' }
        Write-PortalStatus 'installing' "Installazione $($request.targetVersion) e riavvio." $request.requestId $request.targetVersion
        $protected = @('.git', 'cloud/.env', 'cloud/backups', 'cloud/control', 'cloud/data')
        foreach ($item in $manifest.files) {
            $relative = ($item.path -replace '\\', '/').TrimStart('/')
            if ($protected | Where-Object { $relative -eq $_ -or $relative.StartsWith("$_/") }) { throw 'Il pacchetto tenta di modificare dati protetti.' }
            $source = Join-Path $stageDir $relative
            $target = Join-Path $ProjectDir $relative
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $source -Destination $target -Force
        }
        foreach ($relative in $manifest.removedFiles) {
            $target = Join-Path $ProjectDir $relative
            if (Test-Path -LiteralPath $target -PathType Leaf) { Remove-Item -LiteralPath $target -Force }
        }
        try {
            Invoke-Compose @('up', '-d', '--build', 'app')
            Wait-PortalHealthy
        } catch {
            & tar.exe -xzf $sourceBackup -C $ProjectDir
            Invoke-Compose @('up', '-d', '--build', 'app')
            Write-PortalStatus 'error' 'Aggiornamento non riuscito; file precedenti ripristinati.' $request.requestId
            throw
        }
        Write-PortalStatus 'completed' "Versione $($request.targetVersion) installata correttamente. Backup conservati." $request.requestId $request.targetVersion
        if ($request.source -eq 'upload') { Remove-Item -LiteralPath (Join-Path $ControlDir $request.filePath) -Force -ErrorAction SilentlyContinue }
        Remove-Item -LiteralPath $workDir -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        $failedRequestId = if ($request -and $request.requestId) { [string]$request.requestId } else { '' }
        $failedVersion = if ($request -and $request.targetVersion) { [string]$request.targetVersion } else { '' }
        Write-PortalStatus 'error' $_.Exception.Message $failedRequestId $failedVersion
    } finally {
        Remove-Item -LiteralPath $ProcessingFile -Force -ErrorAction SilentlyContinue
    }
}
