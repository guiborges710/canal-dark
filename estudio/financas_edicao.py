"""Edicao local e validada de um movimento financeiro no CSV do usuario."""
import csv
import hashlib
import re
import shutil
import threading
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .config import REPO

COLUNAS = ["data", "tipo", "categoria", "descricao", "valor", "status"]
ARQUIVO = REPO / "financas" / "movimentos.csv"
BACKUPS = REPO / "estudio" / "dados" / "financas-backups"
TRAVA = threading.RLock()


class EdicaoRecusada(ValueError):
    def __init__(self, mensagem, codigo=400):
        super().__init__(mensagem)
        self.codigo = codigo


def _valor_centavos(txt):
    try:
        valor = Decimal(str(txt).strip())
        if not valor.is_finite() or valor < 0 or valor > Decimal("100000000"):
            raise InvalidOperation
        centavos = valor.quantize(Decimal("0.01"))
        if centavos != valor:
            raise InvalidOperation
        return int(centavos * 100)
    except (InvalidOperation, ValueError, TypeError):
        raise EdicaoRecusada("Informe um valor positivo com até duas casas decimais.")


def _registro_esperado(reg):
    if not isinstance(reg, dict):
        raise EdicaoRecusada("Não consegui conferir o lançamento atual.", 409)
    try:
        datetime.strptime(str(reg["data"]), "%Y-%m-%d")
        tipo = str(reg["tipo"])
        categoria = str(reg["categoria"])
        descricao = str(reg["descricao"])
        status = str(reg["status"])
        valor = int(reg["valor"])
    except (KeyError, TypeError, ValueError):
        raise EdicaoRecusada("O lançamento mudou ou está incompleto. Recarregue a tela.", 409)
    return {"data": str(reg["data"]), "tipo": tipo, "categoria": categoria,
            "descricao": descricao, "valor_centavos": valor, "status": status}


def editar(payload):
    """Serializa edicoes para impedir que duas gravacoes locais se sobrescrevam."""
    with TRAVA:
        return _editar(payload)


def _editar(payload):
    """Atualiza somente a linha identificada, depois de validar a versão esperada."""
    if not isinstance(payload, dict):
        raise EdicaoRecusada("Pedido de edição inválido.")
    try:
        linha = int(payload.get("linha_csv"))
    except (TypeError, ValueError):
        raise EdicaoRecusada("Não consegui identificar este lançamento.", 409)
    if linha < 2:
        raise EdicaoRecusada("Não consegui identificar este lançamento.", 409)

    esperado = _registro_esperado(payload.get("original"))
    novo = payload.get("alterado")
    if not isinstance(novo, dict):
        raise EdicaoRecusada("Preencha os campos antes de salvar.")

    try:
        data = str(novo.get("data", ""))
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise EdicaoRecusada("Use uma data válida.")
    categoria = str(novo.get("categoria", "")).strip()
    descricao = str(novo.get("descricao", "")).strip()
    status = str(novo.get("status", "")).strip().lower()
    tipo = esperado["tipo"]
    if not categoria or len(categoria) > 80:
        raise EdicaoRecusada("A categoria precisa ter de 1 a 80 caracteres.")
    if not descricao or len(descricao) > 200 or "\n" in descricao or "\r" in descricao:
        raise EdicaoRecusada("A descrição precisa ter de 1 a 200 caracteres, em uma linha.")
    if status not in ({"pago", "a pagar"} if tipo == "gasto" else {"pago", "a receber"}):
        raise EdicaoRecusada("O status não combina com o tipo deste lançamento.")
    valor_centavos = _valor_centavos(novo.get("valor"))
    atual = {"data": data, "tipo": tipo, "categoria": categoria, "descricao": descricao,
             "valor_centavos": valor_centavos, "status": status}

    try:
        with ARQUIVO.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != COLUNAS:
                raise EdicaoRecusada("O cabeçalho de movimentos.csv mudou; nenhum dado foi salvo.", 409)
            linhas = list(reader)
            if any(None in linha or any(valor is None for valor in linha.values()) for linha in linhas):
                raise EdicaoRecusada("movimentos.csv tem uma linha fora do formato; corrija o CSV antes de editar.", 409)
    except OSError as e:
        raise EdicaoRecusada(f"Não consegui ler movimentos.csv: {e}", 500)

    indice = linha - 2
    if indice >= len(linhas):
        raise EdicaoRecusada("O lançamento não está mais nesta posição. Recarregue a tela.", 409)
    linha_csv = linhas[indice]
    try:
        valor_atual = _valor_centavos(linha_csv["valor"])
        compara = {"data": linha_csv["data"], "tipo": linha_csv["tipo"].lower(),
                   "categoria": linha_csv["categoria"] or "sem categoria", "descricao": linha_csv["descricao"],
                   "valor_centavos": valor_atual, "status": linha_csv["status"].lower()}
    except (KeyError, EdicaoRecusada):
        raise EdicaoRecusada("Não consegui conferir o lançamento. Recarregue a tela.", 409)
    if compara != esperado:
        raise EdicaoRecusada("Este lançamento mudou desde que a tela foi aberta. Recarregue e tente de novo.", 409)

    linha_csv.update({"data": atual["data"], "categoria": atual["categoria"],
                      "descricao": atual["descricao"], "valor": f"{valor_centavos // 100}.{valor_centavos % 100:02d}",
                      "status": atual["status"]})
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / f"movimentos-{datetime.now():%Y%m%d-%H%M%S-%f}.csv"
    shutil.copy2(ARQUIVO, backup)
    temporario = ARQUIVO.with_name("movimentos.csv.tmp")
    try:
        with temporario.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COLUNAS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(linhas)
        temporario.replace(ARQUIVO)
    finally:
        temporario.unlink(missing_ok=True)
    return {"ok": True, "backup": backup.name,
            "sha256": hashlib.sha256(ARQUIVO.read_bytes()).hexdigest()}


def restaurar_backup(nome, sha256_atual):
    """Restaura somente um backup gerado pelo próprio editor."""
    if (not isinstance(nome, str) or not re.fullmatch(r"movimentos-\d{8}-\d{6}-\d+\.csv", nome)
            or not isinstance(sha256_atual, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256_atual)):
        raise EdicaoRecusada("Não consegui restaurar o arquivo original.", 500)
    origem = (BACKUPS / nome).resolve()
    raiz = BACKUPS.resolve()
    if origem.parent != raiz or not origem.is_file():
        raise EdicaoRecusada("Não consegui restaurar o arquivo original.", 500)
    atual_hash = hashlib.sha256(ARQUIVO.read_bytes()).hexdigest()
    if atual_hash != sha256_atual:
        raise EdicaoRecusada("O arquivo mudou depois da edição; preservei a versão mais recente.", 409)
    temporario = ARQUIVO.with_name("movimentos.csv.restore.tmp")
    try:
        shutil.copy2(origem, temporario)
        temporario.replace(ARQUIVO)
    finally:
        temporario.unlink(missing_ok=True)
