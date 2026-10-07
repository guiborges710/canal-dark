@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate
pip install kokoro-onnx soundfile numpy
if not exist models mkdir models
if not exist models\kokoro-v1.0.int8.onnx curl -L -o models\kokoro-v1.0.int8.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
if not exist models\voices-v1.0.bin curl -L -o models\voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
xcopy /E /I /Y exemplo\a-erupcao-do-krakatoa-em-1883 output\a-erupcao-do-krakatoa-em-1883
python run.py video --topic "A erupção do Krakatoa em 1883"
start "" output\a-erupcao-do-krakatoa-em-1883
pause
