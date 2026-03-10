from flask import render_template
from app.models.busca_model import ler_csv

class BuscaController:
    def executar(self):
        dados = ler_csv()
        if not dados:
            return render_template("listar.html", pessoa=None, restante=0)
        return render_template("listar.html", pessoa=dados[0], restante=len(dados))