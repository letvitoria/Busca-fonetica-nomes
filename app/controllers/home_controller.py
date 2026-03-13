from flask import render_template, jsonify, request, redirect, url_for
from app.models.busca_model import ler_csv, registrar_decisao_e_remover, montar_campos_exibicao

class HomeController:
    def _render_primeiro_registro(self):
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

    def index(self):
        return render_template("listar.html")

    def listar(self):
            return self._render_primeiro_registro()
    
    def csv_data(self):
            """Retorna a página formatada com o primeiro registro pendente"""
            return self._render_primeiro_registro()
    
    def decidir(self):
        decisao = request.form.get('decisao', '')
        if decisao in ('sim', 'nao'):
            registrar_decisao_e_remover(decisao)
        return redirect(url_for('home.csv_data'))

    def relatorio(self):
        return render_template("relatorio.html")
