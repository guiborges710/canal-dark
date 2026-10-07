@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .claude\agents mkdir .claude\agents
for %%F in (pesquisador-nicho.md pesquisador-tema.md estrategista-angulo.md roteirista.md revisor-fatos.md diretor-arte.md editor-metadados.md auditor-conformidade.md) do (
  if exist ".claude\agents\%%F" del /Q ".claude\agents\%%F"
  if exist "agentes_para_instalar\%%F" del /Q "agentes_para_instalar\%%F"
)
copy /Y agentes_para_instalar\*.md .claude\agents\ >nul
echo Agentes instalados em .claude\agents. Pode fechar esta janela.
pause
