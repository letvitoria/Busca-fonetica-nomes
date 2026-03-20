import os
import pandas as pd
from app.service.foto_api_service import extrair_e_salvar_foto

#Triangulação de Dados

def processar_decididos():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Caminho correto para o CSV que o seu HomeController gera
    csv_path = os.path.join(base_path, "..", "models", "decididos.csv")

    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado em: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    matches = df[df['decisao'].str.lower() == 'sim']

    print(f"--- Processando {len(matches)} matches confirmados ---")

    for _, linha in matches.iterrows():
        nome = linha['nome_ro_civil']
        mae = linha.get('mae_ro_civil', 'NÃO INFORMADO')
        pai = linha.get('pai_ro_civil', 'NÃO INFORMADO')

        print(f">> Buscando API: {nome}")
        extrair_e_salvar_foto(nome, pai, mae)

if __name__ == "__main__":
    processar_decididos()