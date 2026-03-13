import csv
import os
import pandas as pd


def _valor_exibicao(valor):
    if valor is None:
        return 'NÃO INFORMADO'

    texto = str(valor).strip()
    if not texto or texto.lower() in ('nan', 'none', 'null'):
        return 'NÃO INFORMADO'

    return valor


def montar_campos_exibicao(pessoa: dict):
    """Monta campos completos para exibição na tela, por base, com fallback legado."""
    pessoa = pessoa or {}

    campos_bnmp = {}
    campos_ro_civil = {}

    for chave, valor in pessoa.items():
        if chave.startswith('bnmp_'):
            campos_bnmp[chave[len('bnmp_'):]] = _valor_exibicao(valor)
        elif chave.startswith('ro_civil_'):
            campos_ro_civil[chave[len('ro_civil_'):]] = _valor_exibicao(valor)

    # Compatibilidade com arquivo antigo (sem prefixos de base)
    if not campos_bnmp:
        mapa_legado_bnmp = {
            'id_bnmp': 'id',
            'nome_bnmp': 'nome',
            'mae_bnmp': 'nome_mae',
            'pai_bnmp': 'nome_pai',
            'bnmp_campo': 'bnmp',
        }
        for chave_legada, nome_saida in mapa_legado_bnmp.items():
            if chave_legada in pessoa:
                campos_bnmp[nome_saida] = _valor_exibicao(pessoa.get(chave_legada))

    if not campos_ro_civil:
        mapa_legado_civil = {
            'id_ro_civil': 'processo',
            'nome_ro_civil': 'nome',
            'mae_ro_civil': 'nome_mae',
            'pai_ro_civil': 'nome_pai',
            'cpf_ro_civil': 'cpf',
            'rg_ro_civil': 'rg',
        }
        for chave_legada, nome_saida in mapa_legado_civil.items():
            if chave_legada in pessoa:
                campos_ro_civil[nome_saida] = _valor_exibicao(pessoa.get(chave_legada))

    nome_bnmp = campos_bnmp.get('Nome') or campos_bnmp.get('nome') or _valor_exibicao(pessoa.get('nome_bnmp'))
    nome_ro_civil = campos_ro_civil.get('nome') or campos_ro_civil.get('Nome') or _valor_exibicao(pessoa.get('nome_ro_civil'))

    return {
        'campos_bnmp': campos_bnmp,
        'campos_ro_civil': campos_ro_civil,
        'nome_bnmp': nome_bnmp,
        'nome_ro_civil': nome_ro_civil,
    }

def ler_csv():
    # Caminho dinâmico para encontrar o arquivo na mesma pasta do model
    caminho = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')
    
    if os.path.exists(caminho):
        # Lemos o CSV e convertemos para uma lista de dicionários
        df = pd.read_csv(caminho)
        return df.to_dict(orient='records')
    return []


def registrar_decisao_e_remover(decisao: str):
    """Salva a decisão do primeiro registro e o remove da fila pendente."""
    caminho = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')
    caminho_decididos = os.path.join(os.path.dirname(__file__), 'decididos.csv')

    if not os.path.exists(caminho):
        return

    df = pd.read_csv(caminho)
    if df.empty:
        return

    primeiro = df.iloc[[0]].copy()
    primeiro['decisao'] = decisao

    # Acrescenta ao arquivo de decididos
    escrever_cabecalho = not os.path.exists(caminho_decididos)
    primeiro.to_csv(caminho_decididos, mode='a', header=escrever_cabecalho, index=False)

    # Remove o primeiro registro da fila
    df.iloc[1:].to_csv(caminho, index=False)

# def executar_busca():
#     # Função temporariamente desativada
#     # A busca fonética será implementada depois.
#     print("Busca desativada temporariamente.")
#     return None

# def ler_csv():
#     """Lê arquivo CSV e retorna lista de dicionários"""
#     csv_path = os.path.join(os.path.dirname(__file__), 'pendentes_validacao_filiacao.csv')
    
#     if not os.path.exists(csv_path):
#         return []
    
#     dados = []
#     try:
#         with open(csv_path, 'r', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 dados.append(row)
#     except Exception as e:
#         print(f"Erro ao ler CSV: {e}")
    
#     return dados