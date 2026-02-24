from flask import redirect, url_for
from app.models.busca_model import executar_busca

class BuscaController:
    def executar(self):
        executar_busca()  #Roda script de busca fonética
        return redirect("/listar")