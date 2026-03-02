from flask import render_template, jsonify
from app.models.busca_model import ler_csv

class HomeController:
    def index(self):
        return render_template("index.html")

    def listar(self):
            dados = ler_csv() # Busca os dados do CSV
            return render_template("listar.html", pessoas=dados)
    
    def csv(self):
        dados = ler_csv() # Busca os dados do CSV
        return render_template("csv.html", dados=dados)
    
    def csv_data(self):
            """Agora retorna a página formatada com os dados do CSV"""
            dados = ler_csv()
            # Enviamos os dados para o listar.html sob a variável 'pessoas'
            return render_template("listar.html", pessoas=dados)
    
    def relatorio(self):
        return render_template("relatorio.html")