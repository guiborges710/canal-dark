@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .claude\agents mkdir .claude\agents
copy /Y agentes_para_instalar\*.md .claude\agents\ >nul
echo Agentes instalados em .claude\agents. Pode fechar esta janela.
pause
