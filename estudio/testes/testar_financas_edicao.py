"""Testes isolados da edição local; todos os arquivos ficam em diretório temporário."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from estudio import financas_edicao as edicao


COLUNAS = edicao.COLUNAS
ORIGINAL = {
    "data": "2026-11-10", "tipo": "gasto", "categoria": "sem categoria",
    "descricao": "Pagamento ficticio", "valor": 20800, "status": "pago",
}


class EdicaoFinancasTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.arquivo = raiz / "movimentos.csv"
        self.backups = raiz / "backups"
        self._gravar([
            {"data": "2026-11-10", "tipo": "gasto", "categoria": "", "descricao": "Pagamento ficticio", "valor": "208.00", "status": "pago"},
            {"data": "2026-11-09", "tipo": "recebido", "categoria": "rendimento", "descricao": "Entrada ficticia", "valor": "0.08", "status": "pago"},
        ])
        self.patchers = [
            patch.object(edicao, "ARQUIVO", self.arquivo),
            patch.object(edicao, "BACKUPS", self.backups),
        ]
        for item in self.patchers:
            item.start()

    def tearDown(self):
        for item in reversed(self.patchers):
            item.stop()
        self.tmp.cleanup()

    def _gravar(self, linhas):
        with self.arquivo.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COLUNAS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(linhas)

    def _pedido(self, **alteracoes):
        novo = {"data": ORIGINAL["data"], "categoria": "transporte", "descricao": "Corrida ficticia", "valor": "42.50", "status": "pago"}
        novo.update(alteracoes)
        return {"linha_csv": 2, "original": dict(ORIGINAL), "alterado": novo}

    def _linhas(self):
        with self.arquivo.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_edita_so_a_linha_alvo_e_preserva_backup(self):
        conteudo_antes = self.arquivo.read_bytes()
        resultado = edicao.editar(self._pedido())
        linhas = self._linhas()
        self.assertEqual(linhas[0]["descricao"], "Corrida ficticia")
        self.assertEqual(linhas[0]["categoria"], "transporte")
        self.assertEqual(linhas[0]["valor"], "42.50")
        self.assertEqual(linhas[0]["tipo"], "gasto")
        self.assertEqual(linhas[1]["descricao"], "Entrada ficticia")
        self.assertEqual((self.backups / resultado["backup"]).read_bytes(), conteudo_antes)

    def test_recusa_linha_alterada_desde_a_leitura(self):
        linhas = self._linhas()
        linhas[0]["descricao"] = "Alterado fora da tela"
        self._gravar(linhas)
        antes = self.arquivo.read_bytes()
        with self.assertRaises(edicao.EdicaoRecusada) as erro:
            edicao.editar(self._pedido())
        self.assertEqual(erro.exception.codigo, 409)
        self.assertEqual(self.arquivo.read_bytes(), antes)
        self.assertFalse(self.backups.exists())

    def test_recusa_valor_e_data_invalidos_sem_gravar(self):
        antes = self.arquivo.read_bytes()
        for alteracao in ({"valor": "42.501"}, {"data": "2026-02-30"}):
            with self.subTest(alteracao=alteracao), self.assertRaises(edicao.EdicaoRecusada):
                edicao.editar(self._pedido(**alteracao))
            self.assertEqual(self.arquivo.read_bytes(), antes)

    def test_recusa_status_incompativel_com_gasto(self):
        antes = self.arquivo.read_bytes()
        with self.assertRaises(edicao.EdicaoRecusada):
            edicao.editar(self._pedido(status="a receber"))
        self.assertEqual(self.arquivo.read_bytes(), antes)

    def test_recusa_indice_fora_do_csv(self):
        pedido = self._pedido()
        pedido["linha_csv"] = 99
        with self.assertRaises(edicao.EdicaoRecusada) as erro:
            edicao.editar(pedido)
        self.assertEqual(erro.exception.codigo, 409)


if __name__ == "__main__":
    unittest.main()
