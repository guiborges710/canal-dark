@echo off
chcp 65001 >nul
cd /d "%~dp0"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg nao encontrado.
  echo Instale com este comando no terminal: winget install Gyan.FFmpeg
  echo Depois FECHE e ABRA o terminal e rode este arquivo de novo.
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado.
  echo Instale em python.org e marque a opcao "Add python.exe to PATH".
  pause
  exit /b 1
)

python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env

echo.
echo Instalacao concluida. Proximo passo: de dois cliques em teste_simulado.bat
pause
