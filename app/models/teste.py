import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from rapidfuzz import fuzz #Utilizando rapidfuzz pela velocidade
from unicodedata import unidecode

def padroniza_texto(texto):
    #Remover acentos e espaços
    return unidecode(str(texto)).strip().lower() if texto else ""
# 1 - Carregar os dados 
#Preimeiro banco de dados (O Maior) Base civil de Rondônia
conn_civilro = sqlite3.connect('Busca-fonetica-nomes/app/models/bases/ro_civil.db')
df_civil = pd.read_sql_query("SELECT id, nome FROM pessoas", conn_civilro)
conn_civilro.close()
#Segundo baco de dados (BNMP)
conn_bnmp = sqlite3.connect('Busca-fonetica-nomes/app/models/bases/bnmp.db')
df_bnmp = pd.read_sql_query("SELECT id, Nome FROM dados_csv", conn_bnmp)
conn_bnmp.close()
#Conexão fechada

#Padronização para vetorização
"""
A vetorização de um banco de dados converte dados não estruturados (texto, imagem, áudio) 
em representações numéricas (vetores/embeddings) que capturam seu significado semântico
"""

nomes_referencia = df_civil['nome'].apply(padroniza_texto).tolist()
#Passo 2: Vetorização (scikitlearn)
#Os nomes são analizados em grupos de três letras (n-gramas)
#Como criar a vetorização do DB?
vetorizar = TfidfVectorizer(analyzer='char', ngram_range=(2,3)) #Rande 2 e 3 
tf_idf_matrix = vetorizar.fit_transform(nomes_referencia)

#Cria-se um modelo de "Vizinhos mais próximos"
# n_neighbors=5 Define que buscaremos os 5 mais parecidos no Banco A para cada nome do Banco B
model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
model.fit(tf_idf_matrix)

#Passo 3 Busca e Refinamento
resultados_para_humano = []
for idx, linha_civil in df_civil.iterrows():
    nome_busca = padroniza_texto(linha_civil['nome'])
    #Tranforma o nome de busca em vetor
    vetor_busca = vetorizar.transform([nome_busca])

    #Encontra os índices dos 5 candidatos mais próximos: distancias, indices = model.kneighbors(vetor_busca)
    distancias, indices = model.kneighbors(vetor_busca)
    for i in indices[0]:
        candidato_nome = df_civil.iloc[i]['nome']
        candidato_id = df_civil.iloc[i]['id']

        #Refinamento com Fuzzy para precição prescrita
        score_final = fuzz.ratio(nome_busca, padroniza_texto(candidato_nome))

        #Condicional: Retornar apenas os nomes com score acima de 70
        if score_final < 70:
            resultados_para_humano.append({
                'id_civil': linha_civil['id'],
                'nome_civil': linha_civil['nome'],
                'id_bnmo': candidato_id,
                'nome_bnmp': candidato_nome,
                'score': round(score_final, 2)
            })
# Passo 3 Exportar para validação
df_final = pd.DataFrame(resultados_para_humano)
df_final.to_csv('pendentes_validacao.csv', index=False, encoding='utf-8-sig')
print("Varredura concluída. Arquivo 'pendentes_validacao.csv' gerado.")