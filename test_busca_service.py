import unittest

from app.service.busca_service import normalizar_nome_para_comparacao


class TestBuscaService(unittest.TestCase):
    def test_normalizar_nome_para_comparacao_remove_acentos_e_espacos_extras(self):
        nome_a = "  LUIZ   CÁRLOS   RUIZ  "
        nome_b = "luiz carlos ruiz"

        self.assertEqual(
            normalizar_nome_para_comparacao(nome_a),
            normalizar_nome_para_comparacao(nome_b),
        )

    def test_normalizar_nome_para_comparacao_lida_com_nulos_textuais(self):
        self.assertEqual(normalizar_nome_para_comparacao(None), "")
        self.assertEqual(normalizar_nome_para_comparacao("None"), "")
        self.assertEqual(normalizar_nome_para_comparacao("nan"), "")


if __name__ == '__main__':
    unittest.main()
