import csv
import os
import pandas as pd

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