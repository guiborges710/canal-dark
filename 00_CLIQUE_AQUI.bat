@echo off
REM Ecossistema - Subir com tunel seguro

cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║       ECOSSISTEMA - SERVIDOR COM TUNEL NGROK      ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo [INFO] Iniciando servidor e tunel...
echo.

cd /d "%~dp0ecossistema\app"

echo [1/2] Servidor HTTP na porta 8000...
start /B python -m http.server 8000

timeout /t 2 /nobreak

echo [2/2] Ativando tunel ngrok...
echo.
echo ┌────────────────────────────────────────────────────┐
echo │ AGUARDE A URL APARECER ABAIXO                      │
echo │ Copie: https://...ngrok.io                         │
echo │ Cole no navegador do celular                       │
echo │ Login: guilherme / ecossistema123                  │
echo └────────────────────────────────────────────────────┘
echo.

ngrok http 8000

echo.
echo [ERRO] Tunel fechou. Feche esta janela.
pause
