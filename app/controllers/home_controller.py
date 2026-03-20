from flask import render_template, request, redirect, url_for, session

from app.models.busca_model import obter_primeiro_e_total_pendencias, registrar_decisao_e_remover, montar_campos_exibicao 
from app.service.foto_api_service import  buscar_foto_na_api_render

class HomeController:
    def _render_primeiro_registro(self):
        salvo = request.args.get('salvo')
        decisao = request.args.get('decisao', '').lower()

        if 'indice_atual' not in session:
            session['indice_atual'] = 1

        feedback = None
        if salvo == '1' and decisao in ('sim', 'nao'):
            feedback = f"Análise salva com sucesso: {decisao.upper()}."
            session['indice_atual'] += 1

        pessoa, total = obter_primeiro_e_total_pendencias()
        
        if not pessoa:
            return render_template("listar.html", pessoa=None, restante=0, feedback=feedback)

        # Buscamos a foto usando os dados que vieram do CSV (Base Civil de RO)
        foto_base64 = buscar_foto_na_api_render(
            pessoa.get('nome_ro_civil'),
            pessoa.get('pai_ro_civil'),
            pessoa.get('mae_ro_civil')
        )

        dados_exibicao = montar_campos_exibicao(pessoa)

        return render_template(
            "listar.html",
            pessoa=pessoa,
            restante=total,
            indice_atual=session.get('indice_atual', 1),
            feedback=feedback,
            foto_ro_base64=foto_base64, # ENVIA A FOTO PARA O HTML
            **dados_exibicao
        )

    def csv_data(self):
        return self._render_primeiro_registro()

    def decidir(self):
        decisao = request.form.get('decisao', '')
        salvo = False
        if decisao in ('sim', 'nao'):
            salvo = registrar_decisao_e_remover(decisao)
        return redirect(url_for('home.csv_data', salvo='1' if salvo else '0', decisao=decisao))
    def index(self):
        return self._render_primeiro_registro()

    def listar(self):
            return self._render_primeiro_registro()
    


    def relatorio(self):
        return render_template("relatorio.html")

