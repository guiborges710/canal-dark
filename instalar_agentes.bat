@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

set "MODO_SIMULAR=0"
if /I "%~1"=="/simular" set "MODO_SIMULAR=1"
if not "%~1"=="" if /I not "%~1"=="/simular" (
    echo Uso: instalar_agentes.bat [/simular]
    exit /b 2
)

if not exist "agentes_para_instalar\*.md" (
    echo Nenhum agente foi encontrado em agentes_para_instalar.
    exit /b 1
)

if "%MODO_SIMULAR%"=="1" (
    echo SIMULACAO: nenhum arquivo ou pasta sera alterado.
) else (
    if not exist ".claude\agents" mkdir ".claude\agents"
    echo Instalando somente agentes que ainda nao existem.
)

for %%F in ("agentes_para_instalar\*.md") do (
    if exist ".claude\agents\%%~nxF" (
        if "%MODO_SIMULAR%"=="1" (
            echo [PRESERVARIA] %%~nxF - ja existe no destino.
        ) else (
            echo [PRESERVADO] %%~nxF - ja existe no destino.
        )
    ) else (
        if "%MODO_SIMULAR%"=="1" (
            echo [INSTALARIA] %%~nxF
        ) else (
            copy /-Y "%%~fF" ".claude\agents\%%~nxF" >nul
            if errorlevel 1 (
                echo [NAO INSTALADO] %%~nxF - o destino passou a existir ou houve erro de copia.
            ) else (
                echo [INSTALADO] %%~nxF
            )
        )
    )
)

if "%MODO_SIMULAR%"=="1" (
    echo Simulacao concluida. Nada foi alterado.
) else (
    echo Instalacao concluida. Arquivos existentes foram preservados.
)
