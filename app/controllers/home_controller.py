from flask import render_template, request, redirect, url_for, session

from app.models.busca_model import obter_primeiro_e_total_pendencias, registrar_decisao_e_remover, montar_campos_exibicao

class HomeController:
    def _render_primeiro_registro(self):
        salvo = request.args.get('salvo')
        decisao = request.args.get('decisao', '').lower()

        if 'contador_atual' not in session:
            session['contador_atual'] = 1

        indice_atual = session['contador_atual']

        feedback = None
        if salvo == '1' and decisao in ('sim', 'nao'):
            feedback = f"Análise salva com sucesso: {decisao.upper()}."
        elif salvo == '0' and decisao in ('sim', 'nao'):
            feedback = "Não havia registro pendente para salvar essa decisão."

        pessoa, total = obter_primeiro_e_total_pendencias()
        if not pessoa:
            session.pop('contador_atual', None)
            return render_template(
                "listar.html",
                pessoa=pessoa,
                restante=total,
                indice_atual=0,
                feedback=feedback,
            )

        dados_exibicao = montar_campos_exibicao(pessoa)

        return render_template(
            "listar.html",
            pessoa=pessoa,
            restante=total,
            feedback=feedback,
            indice_atual=indice_atual,
            **dados_exibicao,
        )

    def index(self):
        return self._render_primeiro_registro()

    def listar(self):
            return self._render_primeiro_registro()
    
    def csv_data(self):
            """Retorna a página formatada com o primeiro registro pendente"""
            return self._render_primeiro_registro()
    
    def decidir(self):
        decisao = request.form.get('decisao', '')
        salvo = False
        if decisao in ('sim', 'nao'):
            salvo = registrar_decisao_e_remover(decisao)
            if salvo:
                session['contador_atual'] = session.get('contador_atual', 1) + 1

        return redirect(url_for('home.csv_data', salvo='1' if salvo else '0', decisao=decisao))

    def relatorio(self):
        return render_template("relatorio.html")
