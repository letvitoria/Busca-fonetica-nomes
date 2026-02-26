from flask import render_template, jsonify
from app.models.busca_model import ler_csv

class HomeController:
    def index(self):
        return render_template("index.html")

    def listar(self):
        return render_template("listar.html")
    
    def csv(self):
        return render_template("csv.html")
    
    def csv_data(self):
        """Endpoint que retorna dados do CSV em JSON"""
        dados = ler_csv()
        return jsonify(dados)
    
    def relatorio(self):
        return render_template("relatorio.html")