$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Join-Path $ProjectRoot 'tmp\pyinstaller'
$VirtualEnvironment = Join-Path $BuildRoot 'venv'
$Python = Join-Path $VirtualEnvironment 'Scripts\python.exe'
$Dist = Join-Path $ProjectRoot 'outputs\windows-exe-dist'

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv $VirtualEnvironment
    if ($LASTEXITCODE -ne 0) { throw 'Creazione ambiente Python non riuscita.' }
}

& $Python -m pip install --disable-pip-version-check --quiet --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Aggiornamento pip non riuscito.' }
& $Python -m pip install --disable-pip-version-check --quiet 'pyinstaller>=6,<7' 'pillow>=10,<13'
if ($LASTEXITCODE -ne 0) { throw 'Installazione strumenti di compilazione non riuscita.' }

New-Item -ItemType Directory -Path $Dist -Force | Out-Null

& $Python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name 'Quiz-400-VVF-2026' `
    --icon (Join-Path $ProjectRoot 'logo-vvf.png') `
    --version-file (Join-Path $ProjectRoot 'windows-version-info-app.txt') `
    --distpath $Dist `
    --workpath (Join-Path $BuildRoot 'main-work') `
    --specpath (Join-Path $BuildRoot 'spec') `
    (Join-Path $ProjectRoot 'portable_server.py')
if ($LASTEXITCODE -ne 0) { throw 'Compilazione dell’app EXE non riuscita.' }

& $Python -m PyInstaller --noconfirm --clean --onefile --console `
    --name 'Aggiorna-Quiz-400-VVF-2026' `
    --icon (Join-Path $ProjectRoot 'logo-vvf.png') `
    --version-file (Join-Path $ProjectRoot 'windows-version-info-updater.txt') `
    --distpath $Dist `
    --workpath (Join-Path $BuildRoot 'updater-work') `
    --specpath (Join-Path $BuildRoot 'spec') `
    (Join-Path $ProjectRoot 'update_quiz.py')
if ($LASTEXITCODE -ne 0) { throw 'Compilazione dell’aggiornamento EXE non riuscita.' }

Write-Host "EXE creati in $Dist"
