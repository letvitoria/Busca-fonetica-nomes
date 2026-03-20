from flask import render_template
from app.models.busca_model import ler_csv, montar_campos_exibicao
from app.service.foto_api_service import buscar_foto_na_api_render

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
        foto_base64 = buscar_foto_na_api_render(
            pessoa.get('nome_ro_civil'),
            pessoa.get('pai_ro_civil'),
            pessoa.get('mae_ro_civil')
        )

        return render_template(
            "listar.html",
            pessoa=pessoa,
            restante=len(dados),
            indice_atual=1,
            feedback=None,
            foto_ro_base64=foto_base64,
            **dados_exibicao,
        )