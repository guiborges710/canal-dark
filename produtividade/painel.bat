@echo off
rem Abre o painel do Ronaldo (http://127.0.0.1:8766/). Feche esta janela para desligar o painel.
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" produtividade\painel.py
) else (
  python produtividade\painel.py
)
pause
