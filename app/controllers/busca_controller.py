from flask import render_template
from app.models.busca_model import ler_csv, montar_campos_exibicao

class BuscaController:
    def executar(self):
        dados = ler_csv()
        if not dados:
            return render_template(
                "listar.html",
                pessoa=None,
                restante=0,
                indice_atual=0,
                feedback=None,
            )

        pessoa = dados[0]
        dados_exibicao = montar_campos_exibicao(pessoa)

        return render_template(
            "listar.html",
            pessoa=pessoa,
            restante=len(dados),
            indice_atual=1,
            feedback=None,
            **dados_exibicao,
        )