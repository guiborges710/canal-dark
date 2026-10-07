@echo off
chcp 65001 >nul
cd /d "%~dp0"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg nao encontrado. Instale com: winget install Gyan.FFmpeg
  echo Depois FECHE e ABRA o terminal e rode este arquivo de novo.
  pause
  exit /b 1
)
where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale em python.org marcando "Add python.exe to PATH".
  pause
  exit /b 1
)

if not exist .venv\Scripts\activate.bat (
  echo Criando ambiente Python ^(so na primeira vez^)...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
if errorlevel 1 (
  echo Falha ao instalar as dependencias.
  pause
  exit /b 1
)

if not exist .env (
  echo Falta o arquivo .env. Copie .env.example para .env e preencha CF_ACCOUNT_ID e CF_API_TOKEN.
  pause
  exit /b 1
)

if not exist models mkdir models
if not exist models\kokoro-v1.0.int8.onnx curl -L -o models\kokoro-v1.0.int8.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
if not exist models\voices-v1.0.bin curl -L -o models\voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

xcopy /E /I /Y exemplo\a-erupcao-do-krakatoa-em-1883 output\a-erupcao-do-krakatoa-em-1883
if exist output\a-erupcao-do-krakatoa-em-1883\images rmdir /S /Q output\a-erupcao-do-krakatoa-em-1883\images
if exist output\a-erupcao-do-krakatoa-em-1883\clips rmdir /S /Q output\a-erupcao-do-krakatoa-em-1883\clips
if exist output\a-erupcao-do-krakatoa-em-1883\video.mp4 del output\a-erupcao-do-krakatoa-em-1883\video.mp4

python run.py video --topic "A erupção do Krakatoa em 1883"
start "" output\a-erupcao-do-krakatoa-em-1883
pause
