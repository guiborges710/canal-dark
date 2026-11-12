@echo off
REM Sobe o Ecossistema com tunel ngrok

echo.
echo =================================
echo   SUBINDO ECOSSISTEMA
echo =================================
echo.

cd /d "C:\Users\Guilherme\Documents\canal-dark\ecossistema\app"

REM Inicia servidor HTTP em background
echo [1/2] Iniciando servidor HTTP na porta 8000...
start /B python -m http.server 8000

timeout /t 2 /nobreak

REM Inicia ngrok
echo [2/2] Abrindo tunel ngrok...
echo.
echo Aguarde a URL aparecer abaixo. Copie o link e use no celular/outro PC.
echo.

ngrok http 8000

pause
