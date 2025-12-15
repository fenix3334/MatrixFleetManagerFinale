@echo off
title Matrix Fleet Manager - Sistema Avanzato Parco Auto
color 0A

echo.
echo ========================================
echo    MATRIX FLEET MANAGER - AVVIO
echo ========================================
echo.

cd /d %~dp0

echo [1/4] Controllo ambiente virtuale...
if not exist "venv" (
    echo Creazione ambiente virtuale...
    python -m venv venv
)

echo [2/4] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

echo [3/4] Verifica e installazione dipendenze...
REM Installa le dipendenze solo la prima volta per ridurre i tempi di avvio.
if not exist "venv\.deps_installed" (
    echo Installazione dipendenze in corso...
    pip install -r requirements.txt --quiet
    echo done > venv\.deps_installed
) else (
    echo Dipendenze gia installate.
)

echo [4/4] Inizializzazione database...
REM Crea il database solo se non esiste, evitando aggiornamenti ripetitivi.
if not exist "instance\matrix_fleet.db" (
    echo Creazione nuovo database...
    python init_db.py
) else (
    echo Database esistente: nessuna inizializzazione necessaria.
)

echo.
echo ========================================
echo    AVVIO MATRIX FLEET MANAGER
echo ========================================
echo.

REM Avvia il server Flask in una finestra separata senza aprire il browser immediatamente.
start "Server" /B cmd /c "python main.py"

REM Attende che la porta 5000 sia disponibile prima di aprire il browser per evitare errori ERR_CONNECTION_REFUSED.
powershell -Command "while (-not (Test-NetConnection -ComputerName 'localhost' -Port 5000 -WarningAction SilentlyContinue).TcpTestSucceeded) { Start-Sleep -Seconds 1 } ; Start-Process 'http://localhost:5000'"

echo.
echo ========================================
echo    MATRIX FLEET MANAGER AVVIATO
echo ========================================
echo Premi CTRL+C nella finestra del server per interrompere l'applicazione
pause