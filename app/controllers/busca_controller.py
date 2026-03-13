from flask import render_template
from app.models.busca_model import ler_csv, montar_campos_exibicao

class BuscaController:
    def executar(self):
        dados = ler_csv()
        if not dados:
            return render_template("listar.html", pessoa=None, restante=0)

        pessoa = dados[0]
        dados_exibicao = montar_campos_exibicao(pessoa)

        return render_template(
            "listar.html",
            pessoa=pessoa,
            restante=len(dados),
            **dados_exibicao,
        )