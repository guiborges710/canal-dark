"""Garante que os dois arquivos derivados da tela ficam consistentes em falha."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from estudio.dados import gerar_financas


class GravarFinancasAtomicoTest(unittest.TestCase):
    def test_falha_no_segundo_arquivo_restaura_o_primeiro(self):
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp)
            json_path = saida / "financas.json"
            js_path = saida / "financas.js"
            json_path.write_bytes(b"json anterior")
            js_path.write_bytes(b"js anterior")
            replace_original = Path.replace
            falhou = False

            def replace(path, destino):
                nonlocal falhou
                if Path(destino).name == "financas.js" and not falhou:
                    falhou = True
                    raise OSError("falha ficticia")
                return replace_original(path, destino)

            with patch.object(Path, "replace", replace):
                with self.assertRaises(OSError):
                    gerar_financas.gravar({"gerado_em": "ficticio"}, saida)

            self.assertEqual(json_path.read_bytes(), b"json anterior")
            self.assertEqual(js_path.read_bytes(), b"js anterior")
            self.assertEqual(sorted(p.name for p in saida.iterdir()), ["financas.js", "financas.json"])

    def test_falha_sem_versao_anterior_remove_arquivo_parcial(self):
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp)
            replace_original = Path.replace
            falhou = False

            def replace(path, destino):
                nonlocal falhou
                if Path(destino).name == "financas.js" and not falhou:
                    falhou = True
                    raise OSError("falha ficticia")
                return replace_original(path, destino)

            with patch.object(Path, "replace", replace):
                with self.assertRaises(OSError):
                    gerar_financas.gravar({"gerado_em": "ficticio"}, saida)

            self.assertEqual(list(saida.iterdir()), [])

    def test_falha_ao_gravar_temporario_limpa_o_temporario(self):
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp)
            json_path = saida / "financas.json"
            js_path = saida / "financas.js"
            json_path.write_bytes(b"json anterior")
            js_path.write_bytes(b"js anterior")
            with patch.object(gerar_financas.os, "fsync", side_effect=OSError("falha ficticia")):
                with self.assertRaises(OSError):
                    gerar_financas.gravar({"gerado_em": "ficticio"}, saida)
            self.assertEqual(json_path.read_bytes(), b"json anterior")
            self.assertEqual(js_path.read_bytes(), b"js anterior")
            self.assertEqual(sorted(p.name for p in saida.iterdir()), ["financas.js", "financas.json"])


if __name__ == "__main__":
    unittest.main()
