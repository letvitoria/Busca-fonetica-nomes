import sqlite3
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from rapidfuzz import fuzz
from unidecode import unidecode

# Configuração de caminhos baseada na sua estrutura de pastas
DIR = os.path.dirname(os.path.abspath(__file__))
PATH_RO = os.path.join(DIR, "bases", "ro_civil.db")
PATH_BNMP = os.path.join(DIR, "bases", "bnmp.db")
print("Caminho do banco de dados defnido com sucesso.✅")

def padroniza(texto):
    return unidecode(str(texto)).strip().lower() if texto else ""

# passo 1 carregamento de dados
# Banco Maior (Referência: ro_civil)
conn_civilro = sqlite3.connect(PATH_RO)
print("---Selecionando a primeira tabela ---🔎")
df_civil = pd.read_sql_query("SELECT rowid, nome FROM pessoas", conn_civilro) #Para caso de mudar o índice do DB, trocar por hash
#rowid: identificador único de 64 bits integrado automaticamente a quase todas as tabelas, funcionando como a chave primária física. 
conn_civilro.close()

# Banco Menor (Comparação: bnmp)
conn_bnmp = sqlite3.connect(PATH_BNMP)
df_bnmp = pd.read_sql_query("SELECT id, Nome FROM dados_csv", conn_bnmp) 
conn_bnmp.close()

print(" ---- Verificando Registros Existentes ----")
print(f"Bases carregadas. RO Civil: {len(df_civil)} registros.")
print(f"Bases carregadas. BNMP: {len(df_bnmp)} registros.")
print("---- Iniciando a vetorização.... ----")
# passo 2 vetorização matemática (SCIKIT-LEARN) ---
# Criamos a lista de nomes padronizados para o "treinamento" do vetor
nomes_referencia = df_civil['nome'].apply(padroniza).tolist()

# Transformamos nomes em vetores de 2 e 3 letras (n-grams)
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
tf_idf_matrix = vectorizer.fit_transform(nomes_referencia)

# Modelo para encontrar os 5 vizinhos mais próximos via Similaridade de Cosseno
model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
model.fit(tf_idf_matrix)


resultados_para_humano = []

print("Iniciando varredura inteligente...")

for idx, linha_bnmp in df_bnmp.iterrows():
    nome_alvo = padroniza(linha_bnmp['Nome'])
    
    # Vetoriza o nome do BNMP e busca os 5 candidatos mais parecidos no RO Civil
    vetor_alvo = vectorizer.transform([nome_alvo])
    distancias, indices = model.kneighbors(vetor_alvo)
    
    for i in indices[0]:
        nome_candidato = df_civil.iloc[i]['nome']
        id_candidato = df_civil.iloc[i]['rowid'] #ID de acordo com o index do banco de dados. 
        
        # Refinamento final com RapidFuzz para garantir precisão
        score_final = fuzz.ratio(nome_alvo, padroniza(nome_candidato))
        
        # Se o score for alto, guardamos para o agente humano validar
        if score_final > 75:
            resultados_para_humano.append({
                'id_bnmp': linha_bnmp['id'],
                'nome_bnmp': linha_bnmp['Nome'],
                'id_ro_civil': id_candidato,
                'nome_ro_civil': nome_candidato,
                'score': round(score_final, 2)
            })
print("Iniciando passo 2 (salvamento dos resultados...)")
# --Passo 4 salvamento dos resultados
df_final = pd.DataFrame(resultados_para_humano)
df_final.to_csv(os.path.join(DIR, 'pendentes_validacao.csv'), index=False, encoding='utf-8-sig')

print(f"Concluído! {len(df_final)} possíveis similaridades encontradas.")