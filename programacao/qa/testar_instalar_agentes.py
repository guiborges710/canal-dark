"""Teste isolado do instalar_agentes.bat (PROG-010).

O instalador e seus dados são copiados para uma pasta temporária. Assim, este
teste nunca lê nem escreve em .claude/agents do repositório.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
INSTALADOR = RAIZ / "instalar_agentes.bat"


def executar(instalador: Path, *argumentos: str, codigo_esperado: int = 0) -> str:
    resultado = subprocess.run(
        ["cmd.exe", "/d", "/c", str(instalador), *argumentos],
        cwd=instalador.parent,
        input="\n",
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    assert resultado.returncode == codigo_esperado, (
        f"Instalador terminou com código {resultado.returncode}; "
        f"esperado: {codigo_esperado}.\n"
        f"stdout:\n{resultado.stdout}\nstderr:\n{resultado.stderr}"
    )
    return resultado.stdout


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="prog010-") as temporaria:
        caixa = Path(temporaria)
        instalador = caixa / INSTALADOR.name
        shutil.copy2(INSTALADOR, instalador)

        origem = caixa / "agentes_para_instalar"
        destino = caixa / ".claude" / "agents"
        origem.mkdir()

        saida_vazia = executar(instalador, codigo_esperado=1)
        assert "Nenhum agente" in saida_vazia
        assert not (caixa / ".claude").exists(), (
            "O instalador criou o destino mesmo sem agentes para instalar."
        )

        destino.mkdir(parents=True)

        (origem / "novo.md").write_text("versão para instalar\n", encoding="utf-8")
        (origem / "existente.md").write_text("cópia antiga\n", encoding="utf-8")
        existente = destino / "existente.md"
        existente.write_text("trabalho atual\n", encoding="utf-8")

        antes = {arquivo.name: arquivo.read_bytes() for arquivo in destino.iterdir()}
        saida_simulacao = executar(instalador, "/simular")
        depois = {arquivo.name: arquivo.read_bytes() for arquivo in destino.iterdir()}

        assert antes == depois, "O modo /simular alterou o destino."
        assert "INSTALARIA" in saida_simulacao.upper(), (
            "A simulação não informou claramente o arquivo que instalaria."
        )
        assert "PRESERVARIA" in saida_simulacao.upper(), (
            "A simulação não informou claramente o arquivo que preservaria."
        )
        assert "novo.md" in saida_simulacao
        assert "existente.md" in saida_simulacao

        saida_real = executar(instalador)
        assert (destino / "novo.md").read_text(encoding="utf-8") == "versão para instalar\n"
        assert existente.read_text(encoding="utf-8") == "trabalho atual\n", (
            "O instalador sobrescreveu um arquivo existente."
        )
        assert "novo.md" in saida_real
        assert "existente.md" in saida_real

    print("OK PROG-010: simulação sem escrita; novo instalado; existente preservado.")


if __name__ == "__main__":
    main()
