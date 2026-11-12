@echo off
rem PROG-024b: atualiza os dados de Financas e abre a tela. Nada e enviado para a internet.
setlocal
cd /d "%~dp0..\.."
".venv\Scripts\python.exe" estudio\dados\gerar_financas.py
if errorlevel 1 (
  echo.
  echo O gerador falhou. Veja a mensagem acima; a tela mostra a ultima leitura com o selo de dados velhos.
)
 powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/financas/' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  start "Corte local" /min ".venv\Scripts\python.exe" -m estudio --pagina financas --nao-abrir
  timeout /t 2 /nobreak >nul
)
start "" "http://127.0.0.1:8765/financas/"
endlocal
