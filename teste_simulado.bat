@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate
python run.py video --topic "teste" --mock
echo.
echo Abrindo a pasta com o video de teste...
start "" "output\mock-teste"
pause
