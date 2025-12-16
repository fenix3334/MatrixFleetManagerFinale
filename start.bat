@echo off
echo =============================================
echo   Matrix Fleet Manager - Avvio Automatico
echo =============================================
echo.

REM Avvia Backend
echo [1/2] Avvio Backend...
start "Backend API" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python run.py"

REM Attendi 5 secondi
timeout /t 5 /nobreak >nul

REM Avvia Frontend
echo [2/2] Avvio Frontend...
start "Frontend Vue" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo =============================================
echo   COMPLETATO!
echo =============================================
echo.
echo Apri il browser e vai a: http://localhost:5173
echo.
echo Premi un tasto per chiudere questa finestra...
pause >nul
