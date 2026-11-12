"""Integração local da rota de edição; usa apenas um CSV temporário inventado."""
import csv
import http.client
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from estudio import financas_edicao, servidor
from estudio.dados import gerar_financas


class RotaEdicaoFinancasTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        self.app = self.raiz / "ecossistema" / "app"
        self.app.mkdir(parents=True)
        (self.app / "index.html").write_text("tela local", encoding="utf-8")
        self.csv = self.raiz / "movimentos.csv"
        with self.csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=financas_edicao.COLUNAS, lineterminator="\n")
            w.writeheader()
            w.writerow({"data": "2026-11-10", "tipo": "gasto", "categoria": "sem categoria", "descricao": "Compra ficticia", "valor": "12.34", "status": "pago"})
        self.original = {"data": "2026-11-10", "tipo": "gasto", "categoria": "sem categoria", "descricao": "Compra ficticia", "valor": 1234, "status": "pago"}
        self.patches = [
            patch.object(servidor, "REPO", self.raiz),
            patch.object(financas_edicao, "ARQUIVO", self.csv),
            patch.object(financas_edicao, "BACKUPS", self.raiz / "backups"),
            patch.object(gerar_financas, "gerar", return_value={"gerado_em": "2026-11-11T12:00:00"}),
            patch.object(gerar_financas, "gravar"),
        ]
        for p in self.patches:
            p.start()
        self.httpd = servidor.ThreadingHTTPServer(("127.0.0.1", 0), servidor.Manipulador)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def _request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8") if body is not None else None
        h = {"Content-Type": "application/json"} if raw is not None else {}
        h.update(headers or {})
        conn.request(method, path, body=raw, headers=h)
        response = conn.getresponse()
        result = response.status, response.read(), conn
        return result

    def _payload(self):
        return {
            "linha_csv": 2,
            "original": self.original,
            "alterado": {"data": "2026-11-10", "categoria": "transporte", "descricao": "Corrida ficticia", "valor": "42.50", "status": "pago"},
        }

    def test_serve_casca_local_e_recusa_traversal_codificado(self):
        codigo, corpo, conn = self._request("GET", "/financas/")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 200)
        self.assertEqual(corpo, b"tela local")
        codigo, corpo, conn = self._request("GET", "/financas/%2e%2e/movimentos.csv")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 400)
        self.assertNotIn(b"Compra ficticia", corpo)
        for caminho in (
            "/financas/%5c..%5cmovimentos.csv",
            "/financas/%252e%252e/movimentos.csv",
        ):
            codigo, corpo, conn = self._request("GET", caminho)
            self.addCleanup(conn.close)
            self.assertEqual(codigo, 400, caminho)
            self.assertNotIn(b"Compra ficticia", corpo)

    def test_symlink_para_fora_da_raiz_nao_e_servito(self):
        fora = self.raiz / "fora.txt"
        fora.write_text("segredo ficticio", encoding="utf-8")
        link = self.app / "escape.txt"
        try:
            os.symlink(fora, link)
        except (OSError, NotImplementedError) as erro:
            self.skipTest(f"symlink indisponivel neste Windows: {erro}")
        codigo, corpo, conn = self._request("GET", "/financas/escape.txt")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 400)
        self.assertNotIn(b"segredo ficticio", corpo)

    def test_host_de_rede_na_rota_local_e_recusado(self):
        codigo, corpo, conn = self._request("GET", "/financas/", headers={"Host": "192.168.1.50"})
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 403)
        self.assertNotIn(b"tela local", corpo)

    def test_dispatch_sistema_so_atende_chaves_declaradas(self):
        codigo, corpo, conn = self._request("GET", "/api/sistema/setores")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 200)
        self.assertIn(b"setores", corpo)
        codigo, corpo, conn = self._request("GET", "/api/sistema/movimentos.csv")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 404)
        self.assertNotIn(b"Compra ficticia", corpo)

    def test_rotas_sistema_recusam_acesso_de_rede_mesmo_com_rede_ativa(self):
        with patch.object(servidor.acesso, "_estado", {"rede": True, "senha": "senha-ficticia"}), \
             patch.object(servidor.acesso, "e_local", return_value=False):
            for host in ("192.168.1.50", "laptop.local"):
                codigo, corpo, conn = self._request(
                    "GET", "/api/sistema/setores", headers={"Host": host}
                )
                self.addCleanup(conn.close)
                self.assertEqual(codigo, 403, host)
                self.assertNotIn(b"setores", corpo)

    def test_post_local_edita_regenera_e_responde_sem_dado_financeiro(self):
        codigo, corpo, conn = self._request("POST", "/api/financas/movimentos/editar", self._payload())
        self.addCleanup(conn.close)
        resposta = json.loads(corpo)
        self.assertEqual(codigo, 200)
        self.assertTrue(resposta["ok"])
        self.assertNotIn("valor", resposta)
        with self.csv.open(encoding="utf-8", newline="") as f:
            linha = next(csv.DictReader(f))
        self.assertEqual(linha["descricao"], "Corrida ficticia")
        gerar_financas.gerar.assert_called_once_with(self.raiz / "financas")
        gerar_financas.gravar.assert_called_once()

    def test_falha_ao_atualizar_dashboard_restaura_csv_original(self):
        antes = self.csv.read_bytes()
        gerar_financas.gravar.side_effect = OSError("falha ficticia")
        codigo, corpo, conn = self._request("POST", "/api/financas/movimentos/editar", self._payload())
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 500)
        self.assertIn(b"lan\xc3\xa7amento original foi restaurado", corpo)
        self.assertEqual(self.csv.read_bytes(), antes)

    def test_rollback_nao_sobrescreve_edicao_externa_concorrente(self):
        conteudo_externo = self.csv.read_bytes().replace(b"Compra ficticia", b"Edicao externa")

        def falhar_apos_edicao(_):
            self.csv.write_bytes(conteudo_externo)
            raise OSError("falha ficticia")

        gerar_financas.gerar.side_effect = falhar_apos_edicao
        codigo, corpo, conn = self._request("POST", "/api/financas/movimentos/editar", self._payload())
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 409)
        self.assertIn(b"preservei a vers\xc3\xa3o mais recente", corpo)
        self.assertEqual(self.csv.read_bytes(), conteudo_externo)

    def test_post_de_origem_externa_e_recusado_sem_editar(self):
        antes = self.csv.read_bytes()
        codigo, _, conn = self._request("POST", "/api/financas/movimentos/editar", self._payload(), {"Origin": "https://fora.invalid"})
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 403)
        self.assertEqual(self.csv.read_bytes(), antes)

    def test_corpo_excessivo_fecha_conexao_sem_tocar_csv(self):
        antes = self.csv.read_bytes()
        conteudo = b"{" + b" " * 16_384
        codigo, corpo, conn = self._request("POST", "/api/financas/movimentos/editar", headers={"Content-Type": "application/json", "Content-Length": str(len(conteudo))}, body=conteudo)
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 413)
        self.assertEqual(self.csv.read_bytes(), antes)

    def test_json_malformado_nao_expoe_erro_e_servidor_recupera(self):
        codigo, corpo, conn = self._request("POST", "/api/financas/movimentos/editar", b"{")
        self.addCleanup(conn.close)
        self.assertEqual(codigo, 500)
        self.assertIn(b"Erro interno. Tente novamente.", corpo)
        self.assertNotIn(b"Expecting property name", corpo)
        conn.request("GET", "/financas/")
        seguinte = conn.getresponse()
        self.assertEqual(seguinte.status, 200)
        self.assertEqual(seguinte.read(), b"tela local")


if __name__ == "__main__":
    unittest.main()
