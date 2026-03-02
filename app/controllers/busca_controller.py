from flask import render_template
from app.models.busca_model import ler_csv

class BuscaController:
    def executar(self):
        model = ler_csv()
        dados = model.obter_dados_confronto()
        
        # 'dados' contém as linhas do CSV com as colunas do BNMP, RO_CIVIL e SCORE
        return render_template("listar.html", pessoas=dados)