from flask import render_template, jsonify, request, redirect, url_for
from app.models.busca_model import ler_csv, registrar_decisao_e_remover

class HomeController:
    def index(self):
        return render_template("listar.html")

    def listar(self):
            dados = ler_csv()
            if not dados:
                return render_template("listar.html", pessoa=None, restante=0)
            return render_template("listar.html", pessoa=dados[0], restante=len(dados))
    
    def csv_data(self):
            """Retorna a página formatada com o primeiro registro pendente"""
            dados = ler_csv()
            if not dados:
                return render_template("listar.html", pessoa=None, restante=0)
            return render_template("listar.html", pessoa=dados[0], restante=len(dados))
    
    def decidir(self):
        decisao = request.form.get('decisao', '')
        if decisao in ('sim', 'nao'):
            registrar_decisao_e_remover(decisao)
        return redirect(url_for('home.csv_data'))

    def relatorio(self):
        return render_template("relatorio.html")