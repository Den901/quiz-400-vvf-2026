@echo off
cd /d "%~dp0"
where py >nul 2>nul && (py -3 update_quiz.py & goto :done)
where python >nul 2>nul && (python update_quiz.py & goto :done)
echo Python 3 non e' installato ed e' necessario per aggiornare Quiz 400 VVF 2026.
choice /C SN /M "Vuoi installarlo ora dal canale ufficiale"
if errorlevel 2 goto :done
where winget >nul 2>nul
if not errorlevel 1 (
  winget install --exact --id Python.Python.3.14 --source winget --accept-package-agreements --accept-source-agreements
) else (
  echo Scaricamento dell'installer ufficiale Python...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$u='https://www.python.org/ftp/python/3.14.7/python-3.14.7-amd64.exe'; $p=Join-Path $env:TEMP 'python-3.14.7-amd64.exe'; Invoke-WebRequest -Uri $u -OutFile $p; Start-Process -FilePath $p -ArgumentList '/passive InstallAllUsers=0 PrependPath=1 Include_test=0' -Wait"
)
if exist "%LocalAppData%\Programs\Python\Python314\python.exe" (
  "%LocalAppData%\Programs\Python\Python314\python.exe" update_quiz.py
  goto :done
)
where py >nul 2>nul && (py -3 update_quiz.py & goto :done)
where python >nul 2>nul && (python update_quiz.py & goto :done)
echo Installazione non completata. Riavvia Windows e riprova.
:done
echo.
pause
