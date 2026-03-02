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