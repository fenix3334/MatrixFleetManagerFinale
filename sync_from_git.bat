@echo off
REM ========================================
REM  SINCRONIZZAZIONE AUTOMATICA DA GITHUB
REM  Matrix Fleet Manager
REM ========================================
echo.
echo ========================================
echo  SINCRONIZZAZIONE DA GITHUB
echo ========================================
echo.

REM Vai alla cartella del progetto
cd /d C:\Users\lucagiuseppe.forti\Desktop\progettoParcoauto

REM Verifica branch corrente
echo [1/4] Verifico branch corrente...
git branch --show-current
echo.

REM Salva eventuali modifiche locali (stash)
echo [2/4] Salvo modifiche locali temporanee...
git stash push -m "Auto-stash before sync %date% %time%"
echo.

REM Scarica modifiche da GitHub
echo [3/4] Scarico modifiche da GitHub...
git fetch origin claude/fix-fleet-manager-errors-dfwgN
echo.

REM Applica modifiche locali
echo [4/4] Applico modifiche locali...
git pull origin claude/fix-fleet-manager-errors-dfwgN
echo.

REM Ripristina modifiche locali salvate (se ce ne sono)
git stash pop 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Ripristinate modifiche locali salvate
    echo.
)

REM Verifica risultato
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo.
    echo   ✅ SINCRONIZZAZIONE COMPLETATA!
    echo.
    echo   I tuoi file sono aggiornati con GitHub
    echo.
) else (
    echo.
    echo   ❌ ERRORE durante la sincronizzazione
    echo.
    echo   Controlla i messaggi sopra per dettagli
    echo.
)
echo ========================================
echo.
echo Premi un tasto per chiudere...
pause >nul
