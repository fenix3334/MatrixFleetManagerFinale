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

echo [3/4] Installazione/aggiornamento dipendenze...
pip install -r requirements.txt --quiet

echo [4/4] Inizializzazione database...
python init_db.py

echo.
echo ========================================
echo    AVVIO MATRIX FLEET MANAGER
echo ========================================
echo.
echo Apertura browser: http://localhost:5000
echo Premi CTRL+C per fermare il server
echo.

start http://localhost:5000
python main.py

echo.
echo ========================================
echo    MATRIX FLEET MANAGER TERMINATO
echo ========================================
pause